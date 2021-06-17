import select
import sys

MICROPYTHON = sys.implementation.name == "micropython"

BCAST_HOST = "255.255.255.255"
LOCAL_HOST = "0.0.0.0"

LOG_PREFIX = "[μNetwork] "

if MICROPYTHON:
    import usocket as socket
    import ujson as json
    import network
    from utime import sleep

    ap_if = network.WLAN(network.AP_IF)
    sta_if = network.WLAN(network.STA_IF)
else:
    import traceback
    import socket
    import json
    from time import sleep


def micropython_only(fn):
    def wrapper(*args, **kwargs):
        if MICROPYTHON:
            return fn(*args, **kwargs)

    return wrapper


class _Peer:
    def __init__(
            self,
            port,
            *,
            ssid: str = None,
            passwd: str = None,
            enable_ap: bool = False,
            namespace: str = "default",
            retry_for: tuple = (),
            retry_delay: float = 5,
            chunksize: int = 1024,
    ):
        """
        :param port:
            The port to use for peer discovery.
        :param ssid:
            (Optional) SSID of a WIFI connection.
        :param passwd:
            (Optional) Password for WIFI connection.
        :param enable_ap:
            (Optional) Enable ESP's own Access Point.
        :param namespace:
            (Optional) The namespace to use for peer discovery.
        :param retry_for:
            (Optional) Retry if any of these Exceptions occur.
        :param retry_delay:
            (Optional) The time in seconds to wait for, before retrying.
        """
        self.port = port
        self.ssid = ssid
        self.passwd = passwd
        self.enable_ap = enable_ap
        self.namespace = namespace
        self.retry_for = retry_for
        self.retry_delay = retry_delay
        self.chunksize = chunksize

        self.peer_sock, self.data_sock = None, None

        self.disconnect()
        self.connect()

    _namespace_bytes, _namespace_size = None, None

    @property
    def namespace(self):
        return self._namespace_bytes.decode()

    @namespace.setter
    def namespace(self, value):
        self._namespace_bytes = value.encode("utf-8")
        self._namespace_size = len(self._namespace_bytes)

    def _handle_error(self, exc=None):
        print(LOG_PREFIX + "\nCrash report:")

        if MICROPYTHON:
            sys.print_exception(exc)
        else:
            traceback.print_exc()

        print(LOG_PREFIX + "Retrying in %d sec…\n" % self.retry_delay)
        sleep(self.retry_delay)

    @property
    @micropython_only
    def network_connected(self):
        return ap_if.isconnected() or sta_if.isconnected()

    @micropython_only
    def _configure_network(self):
        if self.enable_ap:
            ap_if.active(True)
        if self.ssid is not None:
            sta_if.active(True)
            sta_if.scan()
            sta_if.disconnect()
            sta_if.connect(self.ssid, self.passwd)

    @micropython_only
    def wait_for_network(self, *, max_tries=None, refresh_freq_hz=1):
        wait_sec = 1 / refresh_freq_hz
        print(LOG_PREFIX + "Waiting for network...", end="")

        count = 0
        while not self.network_connected:
            count += 1
            sleep(wait_sec)

            if max_tries is not None and count > max_tries:
                print()
                if not self.network_connected:
                    raise OSError(
                        "Couldn't establish a connection even after %d tries."
                        % max_tries
                    )
                return
            else:
                print("%d..." % count, end="")

    @micropython_only
    def _connect_network(self):
        print(
            LOG_PREFIX
            + "Connecting to network… (ssid: %r passwd: %r AP: %r)"
            % (self.ssid, self.passwd, self.enable_ap)
        )

        while True:
            try:
                self._configure_network()
                self.wait_for_network(max_tries=50)
            except self.retry_for as e:
                self._handle_error(e)
                self._disconnect_network()
            else:
                print(LOG_PREFIX + "Connected to network!")
                return

    @micropython_only
    def _disconnect_network(self):
        ap_if.active(False)
        sta_if.active(False)

    def connect(self):
        self._connect_network()

        self.peer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.peer_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if not MICROPYTHON:
            self.peer_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def disconnect(self):
        self._disconnect_network()

        if self.data_sock is not None:
            self.data_sock.close()
            self.data_sock = None

        if self.peer_sock is not None:
            self.peer_sock.close()
            self.peer_sock = None

    def _send(self, msg: bytes, **kwargs):
        raise NotImplementedError

    def _recv(self, **kwargs) -> tuple:
        raise NotImplementedError

    def send(self, msg_bytes: bytes, **kwargs):
        if msg_bytes == b"":
            raise ValueError(
                "You may not send an empty datagram; it's reserved as a peer disconnect signal."
            )
        while True:
            try:
                return self._send(msg_bytes, **kwargs)
            except self.retry_for as e:
                self._handle_error(e)
                self.connect()

    def recv(self, **kwargs) -> tuple:
        while True:
            try:
                return self._recv(**kwargs)
            except self.retry_for as e:
                self._handle_error(e)
                self.connect()

    def send_str(self, msg_str: str, **kwargs):
        return self.send(msg_str.encode(), **kwargs)

    def recv_str(self, **kwargs) -> tuple:
        msg, address = self.recv(**kwargs)
        return msg.decode(), address

    def send_json(self, msg_json, **kwargs):
        return self.send(json.dumps(msg_json).encode(), **kwargs)

    def recv_json(self, **kwargs) -> tuple:
        msg, address = self.recv(**kwargs)
        return json.loads(msg), address

    def __enter__(self):
        return self

    def __exit__(self, e, *args, **kwargs):
        if e in self.retry_for:
            self._handle_error(e)
            self.connect()
            return True
        else:
            self.disconnect()


def _get_local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if not MICROPYTHON:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.connect((BCAST_HOST, 0))
    return sock.getsockname()[0]


class Client(_Peer):
    """
    The client side of a p2p connection.

    When :py:meth:`connect` is called,
    the client find a :py:class:`Server` with the same :py:attr:`port` and :py:attr:`namespace`.

    (:py:meth:`connect` is usually automatically called inside the constructor.)

    Once connected, the client can send/recv messages as usual.
    """

    def find_server(self) -> tuple:
        while True:
            self.peer_sock.sendto(self._namespace_bytes, (BCAST_HOST, self.port))
            try:
                server_addr = self.peer_sock.recv(self.chunksize).decode()
            except OSError:
                continue
            print(LOG_PREFIX + "Found server @ " + server_addr)
            host, port = server_addr.split(":")
            return host, int(port)

    def connect(self):
        super().connect()

        self.peer_sock.settimeout(1)
        self.data_sock.connect(self.find_server())

    def _send(self, msg: bytes):
        while True:
            try:
                return self.data_sock.sendall(msg)
            except OSError:
                self.disconnect()
                self.connect()

    def _recv(self) -> tuple:
        while True:
            data, addr = self.data_sock.recvfrom(self.chunksize)
            if data == b"":
                raise OSError("Connection is closed.")
            return data, addr


class Server(_Peer):
    """
    The server side of a p2p connection.

    For this class, :py:meth:`recv` and siblings are essential in facilitating the peer-discovery mechanism.

    If a :py:class:`Server` instance doesn't call :py:meth:`recv` in its lifetime,
    then it is hidden to other :py:class:`Client` instances on the network.

    :py:meth:`recv` will respond to all peer-discovery requests until a client sends an actual piece of data,
    sent using :py:meth:`send`.

    The :py:attr:`clients` will keep a mapping of client hostnames, to a TCP socket connecting to them.
    """

    def __init__(
            self,
            port,
            *,
            ssid: str = None,
            passwd: str = None,
            enable_ap: bool = False,
            namespace: str = "default",
            retry_for: tuple = (),
            retry_delay: float = 5,
    ):
        self.clients = None
        self._local_ip = None

        super().__init__(
            port,
            ssid=ssid,
            passwd=passwd,
            enable_ap=enable_ap,
            namespace=namespace,
            retry_for=retry_for,
            retry_delay=retry_delay,
        )

    def connect(self):
        super().connect()

        self.clients = {}

        self.peer_sock.bind((LOCAL_HOST, self.port))
        self.data_sock.bind((LOCAL_HOST, 0))
        self.data_sock.listen(1)

        self._local_ip = (
                _get_local_ip() + ":" + str(self.data_sock.getsockname()[1])
        ).encode()

    def _send(self, msg: bytes, *, host=None):
        if host is None:
            socks = self.clients.values()
        else:
            try:
                socks = [self.clients[host]]
            except KeyError:
                raise ValueError(
                    "Client with provided host (%r) does not exist." % host
                )
        for sock in socks:
            sock.sendall(msg)

    def _recv(self) -> tuple:
        while True:
            readable, *_ = select.select([self.data_sock, self.peer_sock], [], [])
            for sock in readable:
                if sock is self.data_sock:
                    data_sock, address = sock.accept()
                    self.clients[address] = data_sock
                    chunk = data_sock.recv(self.chunksize)
                    if chunk == b"":
                        del self.clients[address]
                        continue
                    return chunk, address
                elif sock is self.peer_sock:
                    msg, address = sock.recvfrom(self.chunksize)
                    if msg != self._namespace_bytes:
                        continue
                    self.peer_sock.sendto(self._local_ip, address)
                    print(LOG_PREFIX + "Client @ %s requested discovery" % address[0])
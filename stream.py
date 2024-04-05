from streaming import StreamingServer, StreamingHandler


class Stream:

    def start(self):
        address0 = ('', 8000)
        server0 = StreamingServer(address0, StreamingHandler)
        server0.serve_forever()

import os


class BotCommands:
    def __init__(self, logger, sock, channel):
        self.logger = logger
        self.sock = sock
        self.channel = channel

        self.prefix = f"PRIVMSG #{self.channel} :"

    def __clear_chat(self, sender: str) -> bool:
        self.logger.info(f"COMMAND RECEIVED - !clear - Sender: {sender}")
        self.sock.send(f"{self.prefix}/clear\r\n".encode("utf-8"))

        return True

    def __del_message(self, msg: str, sender: str, msg_id: str) -> bool:
        self.sock.send(f"{self.prefix}/delete {msg_id}\r\n".encode("utf-8"))
        self.sock.send(f"{self.prefix}{sender}: MESSAGE DELETED: {msg}\r\n".encode("utf-8"))

        return True

    def lurker(self, msg: str, sender: str) -> bool:
        if msg.startswith("!lurk"):
            self.logger.info(f"COMMAND RECEIVED - !lurk - Sender: {sender}")
            self.sock.send(f"{self.prefix}Yo, {sender}! {self.channel} wanted me to tell you he thinks you're awesome and thanks for the lurk! Hope you can make it back!!!\r\n".encode("utf-8"))

            return True

    def switch_code(self, msg: str, sender: str) -> bool:
        if msg.startswith("!fc"):
            self.logger.info(f"COMMAND RECEIVED - !fc - Sender: {sender}")
            self.sock.send(f"{self.prefix}{self.channel} told me to tell you his Switch Friend Code is: 8562-2808-8201\r\n".encode('utf-8'))

            return True

    def updog(self, msg: str, sender: str) -> bool:
        if "updog" in msg or "up dog" in msg:
            self.logger.info(f"COMMAND RECEIVED - updog lul - Sender: {sender}")
            self.sock.send(f"{self.prefix}not much, u? {sender}\r\n".encode("utf-8"))

            return True

    def greet(self, target: str, username: str) -> bool:
        if username == target:
            self.logger.info(f"GREETING SENT - {username}")
            self.sock.send(f"{self.prefix}sup, {username}\r\n".encode('utf-8'))

            return True


class ChannelRewards(BotCommands):

    def channel_points_reward(self, msg: str, sender: str, reward_uuid) -> bool:
        if reward_uuid == os.getenv("OUIJA_PHRASE"):
            self.logger.info(f"REDEMPTION RECEIVED - Ouija Phrase - Sender: {sender} - Phrase: {msg}")
            self.sock.send(f"{self.prefix}{self.channel} Phrase submission received! -- {msg}\r\n".encode("utf-8"))

            return True


class AllCommands(ChannelRewards):
    pass

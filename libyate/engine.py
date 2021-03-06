"""
libyate - engine command definitions
"""

from abc import abstractmethod
from datetime import datetime

import libyate.type


_id = id

KW_CLS_MAP = {}


class CommandMeta(libyate.type.DescriptorMeta):
    """Meta class for Yate command objects"""

    def __new__(mcs, name, bases, attrs):
        cls = super(CommandMeta, mcs).__new__(mcs, name, bases, attrs)

        keyword = attrs.get('__keyword__')

        if keyword is not None:
            KW_CLS_MAP[keyword] = cls

        return cls


class Command(object):
    """Object representing an Yate command"""

    __metaclass__ = CommandMeta

    __descriptors__ = None
    __keyword__ = None

    @abstractmethod
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        if self.__keyword__ is None:
            raise NotImplementedError('Unknown keyword for class {0}'
                                      .format(self.__class__.__name__))
        else:
            yield self.__keyword__

        for desc in self.__descriptors__:
            yield desc.to_string(self)

    def __getitem__(self, item):
        return list(self).__getitem__(item)

    def __repr__(self):
        return '{0}.{1}({2})'.format(
            self.__class__.__module__, self.__class__.__name__,
            ', '.join(repr(x.__get__(self, self.__class__))
                      for x in self.__descriptors__))

    def __str__(self):
        return ':'.join(self)

    def __unicode__(self):
        return str(self).decode()


class Connect(Command):
    """Yate connect command

    :param str role: role of this connection: global, channel, play, record,
        playrec
    :param str id: channel id to connect this socket to
    :param str type: type of data channel, assuming audio if missing
    """

    __keyword__ = '%%>connect'

    role = libyate.type.EncodedString()
    id = libyate.type.EncodedString(blank=True)
    type = libyate.type.EncodedString(blank=True)

    # noinspection PyShadowingBuiltins
    def __init__(self, role=None, id=None, type=None):
        super(Connect, self).__init__(role=role, id=id, type=type)


class Error(Command):
    """Yate error command

    :param str original: the original line exactly as received
    """

    __keyword__ = 'Error in'

    original = libyate.type.String()

    def __init__(self, original=None):
        super(Error, self).__init__(original=original)


class Install(Command):
    """Yate install command

    :param priority: priority in chain, use default (100) if missing
    :type priority: str or int
    :param str name: name of the messages for that a handler should be
        installed
    :param str filter_name: name of a variable the handler will filter
    :param str filter_value: matching value for the filtered variable
    """

    __keyword__ = '%%>install'

    priority = libyate.type.Integer(blank=True)
    name = libyate.type.EncodedString()
    filter_name = libyate.type.EncodedString(blank=True)
    filter_value = libyate.type.EncodedString(blank=True)

    def __init__(self, priority=None, name=None, filter_name=None,
                 filter_value=None):
        super(Install, self).__init__(
            priority=priority, name=name, filter_name=filter_name,
            filter_value=filter_value)


class InstallReply(Command):
    """Yate install reply command

    :param priority: priority of the installed handler
    :type priority: str or int
    :param str name: name of the messages asked to handle
    :param success: success of operation
    :type success: str or bool
    """

    __keyword__ = '%%<install'

    priority = libyate.type.Integer()
    name = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, priority=None, name=None, success=None):
        super(InstallReply, self).__init__(
            priority=priority, name=name, success=success)


class Message(Command):
    """Yate message command

    :param str id: obscure unique message ID string generated by Yate
    :param time: time (in seconds) the message was initially created
    :type time: str, int or datetime.datetime
    :param str name: name of the message
    :param str retvalue: default textual return value of the message
    :param kvp: enumeration of the key-value pairs of the message
    :type kvp: dict, list, set, tuple or libyate.type.OrderedDict
    """

    __keyword__ = '%%>message'

    id = libyate.type.EncodedString()
    time = libyate.type.DateTime()
    name = libyate.type.EncodedString()
    retvalue = libyate.type.EncodedString(blank=True)
    kvp = libyate.type.KeyValueList(blank=True)

    # noinspection PyShadowingBuiltins
    def __init__(self, id=None, time=None, name=None, retvalue=None,
                 kvp=None):

        if id is None:
            id = _id(self)

        if time is None:
            time = datetime.utcnow()

        if name is None:
            name = self.__class__.__name__

        super(Message, self).__init__(
            id=id, time=time, name=name, retvalue=retvalue, kvp=kvp)

    def reply(self, processed=False, name=None, retvalue=None, kvp=None):
        """Generate a message reply

        :param bool processed: indication of if the message has been processed
            or it should be passed to the next handler
        :param str name: new name of the message, if empty keep unchanged
        :param str retvalue: new textual return value of the message
        :param kvp: new key-value pairs to set in the message; to delete the
            key-value pair provide just a key name with no equal sign or value
        :type kvp: dict, list, set, tuple or libyate.type.OrderedDict
        :return: A MessageReply object
        :rtype libyate.cmd.MessageReply
        """

        return MessageReply(id=self.id, processed=processed, name=name,
                            retvalue=retvalue, kvp=kvp)


class MessageReply(Command):
    """Yate message reply command

    :param str id: same message ID string received from the message
    :param bool processed: indication of if the message has been processed or
        it should be passed to the next handler
    :param str name: new name of the message, if empty keep unchanged
    :param str retvalue: new textual return value of the message
    :param kvp: new key-value pairs to set in the message; to delete the
        key-value pair provide just a key name with no equal sign or value
    :type kvp: dict, list, set, tuple or libyate.type.OrderedDict
    :return: A MessageReply object
    """

    __keyword__ = '%%<message'

    id = libyate.type.EncodedString(blank=True)
    processed = libyate.type.Boolean()
    name = libyate.type.EncodedString(blank=True)
    retvalue = libyate.type.EncodedString(blank=True)
    kvp = libyate.type.KeyValueList(blank=True)

    # noinspection PyShadowingBuiltins
    def __init__(self, id=None, processed=None, name=None, retvalue=None,
                 kvp=None):
        super(MessageReply, self).__init__(
            id=id, processed=processed, name=name, retvalue=retvalue, kvp=kvp)


class Output(Command):
    """Yate output command

    :param str output: arbitrary unescaped string
    """

    __keyword__ = '%%>output'

    output = libyate.type.String()

    def __init__(self, output=None):
        super(Output, self).__init__(output=output)


class SetLocal(Command):
    """Yate setlocal command

    :param str name: name of the parameter to modify
    :param value: new value to set in the local module instance, empty to just
        query
    :type value: str, int or bool
    """

    __keyword__ = '%%>setlocal'

    name = libyate.type.EncodedString()
    value = libyate.type.EncodedString(blank=True)

    def __init__(self, name=None, value=None):
        super(SetLocal, self).__init__(name=name, value=value)


class SetLocalReply(Command):
    """Yate setlocal reply command

    :param str name: name of the modified parameter
    :param str value: new value of the local parameter
    :param success: success of operation
    :type success: str or bool
    """

    __keyword__ = '%%<setlocal'

    name = libyate.type.EncodedString()
    value = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, name=None, value=None, success=None):
        super(SetLocalReply, self).__init__(
            name=name, value=value, success=success)


class UnInstall(Command):
    """Yate uninstall command

    :param str name: name of the message handler that should be uninstalled
    """

    __keyword__ = '%%>uninstall'

    name = libyate.type.EncodedString()

    def __init__(self, name=None):
        Command.__init__(self, name=name)


class UnInstallReply(Command):
    """Yate uninstall reply command

    :param priority: priority of the previously installed handler
    :type priority: str or int
    :param str name: name of the message handler asked to uninstall
    :param success: success of operation
    :type success: str or bool
    """

    __keyword__ = '%%<uninstall'

    priority = libyate.type.Integer()
    name = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, priority=None, name=None, success=None):
        super(UnInstallReply, self).__init__(
            priority=priority, name=name, success=success)


class UnWatch(Command):
    """Yate unwatch command

    :param str name: name of the message watcher that should be uninstalled
    """

    __keyword__ = '%%>unwatch'

    name = libyate.type.EncodedString()

    def __init__(self, name=None):
        super(UnWatch, self).__init__(name=name)


class UnWatchReply(Command):
    """Yate unwatch reply command

    :param str name: name of the message watcher asked to uninstall
    :param success: success of operation
    :type success: str or bool
    """

    __keyword__ = '%%<unwatch'

    name = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, name=None, success=None):
        super(UnWatchReply, self).__init__(name=name, success=success)


class Watch(Command):
    """Yate watch command

    :param name: name of the messages for that a watcher should be installed
    """

    __keyword__ = '%%>watch'

    name = libyate.type.EncodedString()

    def __init__(self, name=None):
        super(Watch, self).__init__(name=name)


class WatchReply(Command):
    """Yate watch reply command

    :param name: name of the messages asked to watch
    :param success: success of operation
    :type success: str or bool
    """

    __keyword__ = '%%<watch'

    name = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, name=None, success=None):
        super(WatchReply, self).__init__(name=name, success=success)


def from_string(string):
    """Parse the command string and return an Command object

    :param str string: Command string to parse
    :return: An Yate command object
    :rtype: Command
    :raise NotImplementedError: if the keyword in the command string is not
        supported
    """

    keyword, args = string.split(':', 1)

    cmd_cls = KW_CLS_MAP.get(keyword)

    if cmd_cls is None:
        raise NotImplementedError('Keyword "{0}" not implemented'
                                  .format(keyword))

    cmd_obj = cmd_cls.__new__(cmd_cls)
    args = args.split(':', len(cmd_cls.__descriptors__) - 1)

    # Map arguments to descriptors
    for desc, value in zip(cmd_cls.__descriptors__,
                           args):

        # Decode upcoded strings
        if isinstance(desc, libyate.type.EncodedString):
            value = libyate.type.yate_decode(value)

        desc.__set__(cmd_obj, value)

    return cmd_obj

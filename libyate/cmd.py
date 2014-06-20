"""
libyate - command definitions
"""

import libyate.type

_id = id

KW_MAP = {}


class YateCmdMeta(libyate.type.TypeMeta):
    """Meta class for YateCmd"""

    def __new__(mcs, name, bases, attrs):
        cls = super(YateCmdMeta, mcs).__new__(mcs, name, bases, attrs)

        keyword = attrs.get('__keyword__')

        if keyword is not None:
            KW_MAP[keyword] = cls

        return cls


class YateCmd(object):
    """Object representing an Yate command"""

    __keyword__ = None
    __metaclass__ = YateCmdMeta

    def __new__(cls, *args, **kwargs):
        if cls == YateCmd:
            raise NotImplementedError('{0} must be sub-classed'.format(
                cls.__name__))
        else:
            return super(YateCmd, cls).__new__(cls)

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

        for attr in self.__descriptors__():
            yield self.__dict__.get(attr.__name__) or ''

    def __repr__(self):
        return '{0}.{1}{2}'.format(
            self.__class__.__module__, self.__class__.__name__,
            tuple(x.__get__(self, self.__class__)
                  for x in self.__descriptors__()))

    def __str__(self):
        return ':'.join(self).rstrip(':')

    def __unicode__(self):
        return str(self).decode()

    @classmethod
    def __descriptors__(cls):
        return sorted(
            filter(lambda x: isinstance(x, libyate.type.BaseType),
                   (v for k, v in cls.__dict__.items())),
            key=lambda x: x.__instance_number__)


class Connect(YateCmd):
    """Yate connect command"""

    __keyword__ = '%%>connect'

    role = libyate.type.EncodedString()
    id = libyate.type.EncodedString(blank=True)
    type = libyate.type.EncodedString(blank=True)

    def __init__(self, role=None, id=None, type=None):
        super(Connect, self).__init__(role=role, id=id, type=type)


class Error(YateCmd):
    """Yate error command"""

    __keyword__ = 'Error in'

    original = libyate.type.String()

    def __init__(self, original=None):
        super(Error, self).__init__(original=original)


class Install(YateCmd):
    """Yate install command"""

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


class InstallReply(YateCmd):
    """Yate install reply command"""

    __keyword__ = '%%<install'

    priority = libyate.type.Integer()
    name = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, priority=None, name=None, success=None):
        super(InstallReply, self).__init__(
            priority=priority, name=name, success=success)


class Message(YateCmd):
    """Yate message command"""

    __keyword__ = '%%>message'

    id = libyate.type.EncodedString()
    time = libyate.type.DateTime()
    name = libyate.type.EncodedString()
    retvalue = libyate.type.EncodedString(blank=True)
    kvp = libyate.type.KeyValueTuple(blank=True)

    def __init__(self, id=None, time=None, name=None, retvalue=None,
                 kvp=None):

        # Generate random id
        if id is None:
            id = _id(self)

        # Get current time
        if time is None:
            from datetime import datetime
            time = datetime.utcnow()

        # Use class name if name is not specified
        if name is None:
            name = self.__class__.__name__

        super(Message, self).__init__(
            id=id, time=time, name=name, retvalue=retvalue, kvp=kvp)

    def reply(self, processed=False, name=None, retvalue=None, kvp=None):
        """Generate a message reply

        :param processed: boolean ("true" or "false") indication if the
            message has been processed or it should be passed to the next
            handler
        :param name: new name of the message, if empty keep unchanged
        :param retvalue: new textual return value of the message
        :param kvp: new key-value pairs to set in the message; to delete the
            key-value pair provide just a key name with no equal sign or value
        :return: MessageReply
        """
        return MessageReply(id=self.id, processed=processed, name=name,
                            retvalue=retvalue, kvp=kvp)


class MessageReply(YateCmd):
    """Yate message reply command"""

    __keyword__ = '%%<message'

    id = libyate.type.EncodedString()
    processed = libyate.type.Boolean()
    name = libyate.type.EncodedString(blank=True)
    retvalue = libyate.type.EncodedString(blank=True)
    kvp = libyate.type.KeyValueTuple(blank=True)

    def __init__(self, id=None, processed=None, name=None, retvalue=None,
                 kvp=None):
        super(MessageReply, self).__init__(
            id=id, processed=processed, name=name, retvalue=retvalue, kvp=kvp)


class Output(YateCmd):
    """Yate output command"""

    __keyword__ = '%%>output'

    output = libyate.type.String()

    def __init__(self, output=None):
        super(Output, self).__init__(output=output)


class SetLocal(YateCmd):
    """Yate setlocal command"""

    __keyword__ = '%%>setlocal'

    name = libyate.type.EncodedString()
    value = libyate.type.EncodedString(blank=True)

    def __init__(self, name=None, value=None):
        super(SetLocal, self).__init__(name=name, value=value)


class SetLocalReply(YateCmd):
    """Yate setlocal reply command"""

    __keyword__ = '%%<setlocal'

    name = libyate.type.EncodedString()
    value = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, name=None, value=None, success=None):
        super(SetLocalReply, self).__init__(
            name=name, value=value, success=success)


class UnInstall(YateCmd):
    """Yate uninstall command"""

    __keyword__ = '%%>uninstall'

    name = libyate.type.EncodedString()

    def __init__(self, name=None):
        YateCmd.__init__(self, name=name)


class UnInstallReply(YateCmd):
    """Yate uninstall reply command"""

    __keyword__ = '%%<uninstall'

    priority = libyate.type.Integer()
    name = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, priority=None, name=None, success=None):
        super(UnInstallReply, self).__init__(
            priority=priority, name=name, success=success)


class UnWatch(YateCmd):
    """Yate unwatch command"""

    __keyword__ = '%%>unwatch'

    name = libyate.type.EncodedString()

    def __init__(self, name=None):
        super(UnWatch, self).__init__(name=name)


class UnWatchReply(YateCmd):
    """Yate unwatch reply command"""

    __keyword__ = '%%<unwatch'

    name = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, name=None, success=None):
        super(UnWatchReply, self).__init__(name=name, success=success)


class Watch(YateCmd):
    """Yate watch command"""

    __keyword__ = '%%>watch'

    name = libyate.type.EncodedString()

    def __init__(self, name=None):
        super(Watch, self).__init__(name=name)


class WatchReply(YateCmd):
    """Yate watch reply command"""

    __keyword__ = '%%<watch'

    name = libyate.type.EncodedString()
    success = libyate.type.Boolean()

    def __init__(self, name=None, success=None):
        super(WatchReply, self).__init__(name=name, success=success)

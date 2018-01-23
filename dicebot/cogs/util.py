from discord.ext import commands

from .. import model as m


class BotError (Exception):
    pass


class NoCharacterError (BotError):
    pass


class ItemNotFoundError (BotError):
    def __init__(self, value=None):
        self.value = value


class Cog:
    def __init__(self, bot):
        self.bot = bot


def get_character(session, userid, server):
    '''
    Gets a character based on their user
    '''
    character = session.query(m.Character)\
        .filter_by(user=str(userid), server=str(server)).one_or_none()
    if character is None:
        raise NoCharacterError()
    return character


def sql_update(session, type, keys, values):
    '''
    Updates a sql object
    '''
    obj = session.query(type)\
        .filter_by(**keys).one_or_none()
    if obj is not None:
        for value in values:
            setattr(obj, value, values[value])
    else:
        values = values.copy()
        values.update(keys)
        obj = type(**values)
        session.add(obj)

    session.commit()

    return obj


async def send_pages(ctx, paginator):
    for page in paginator.pages:
        await ctx.send(page)


def item_paginator(items, header=None):
    paginator = commands.Paginator(prefix='', suffix='')
    if header:
        paginator.add_line(header)
    for item in items:
        paginator.add_line(str(item))
    return paginator


def desc_paginator(items, header=None):
    paginator = commands.Paginator(prefix='', suffix='')
    if header:
        paginator.add_line(header)
    for item in items:
        paginator.add_line('***{}***'.format(str(item)))
        if item.description:
            for line in item.description.splitlines():
                paginator.add_line(line)
    return paginator


def strip_quotes(arg):
    if len(arg) >= 2 and arg.startswith('"') and arg.endswith('"'):
        arg = arg[1:-1]
    return arg
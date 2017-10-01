from discord.ext import commands
from sqlalchemy.orm.exc import NoResultFound

import model as m
from util import Cog, get_character, sql_update, ItemNotFoundError


def int_or_max(value: str):
    if value == 'max':
        return value
    else:
        try:
            return int(value)
        except ValueError:
            raise commands.BadArgument(value)


class ResourceCog (Cog):
    @commands.group('resource', invoke_without_command=True)
    async def group(self, ctx):
        '''
        Manages character resources
        '''
        await ctx.send('Invalid subcommand')

    @group.command(aliases=['update'])
    async def add(self, ctx, name: str, max_uses: int, recover: str):
        '''
        Adds or changes a character resource

        Parameters:
        [name] the name of the new resource
        [max uses] the maximum number of uses of the resource
        [recover] the rest required to recover the resource,
            can be short|long|other
        '''
        if recover not in ['short', 'long', 'other']:
            raise commands.BadArgument('recover')

        character = get_character(ctx.session, ctx.author.id, ctx.guild.id)

        resource = sql_update(ctx.session, m.Resource, {
            'character': character,
            'name': name,
        }, {
            'max': max_uses,
            'current': max_uses,
            'recover': recover,
        })

        await ctx.send('{} now has {}'.format(
            str(character), str(resource)))

    @group.command()
    async def use(self, ctx, number: int, *, name: str):
        '''
        Consumes 1 use of the resource

        Parameters:
        [number] the quantity of the resource to use
            can be negative to regain, but cannot go above max
        [name] the name of the resource
        '''
        character = get_character(ctx.session, ctx.author.id, ctx.guild.id)

        try:
            resource = ctx.session.query(m.Resource)\
                .filter_by(name=name, character=character).one()
        except NoResultFound:
            raise ItemNotFoundError

        if resource.current - number >= 0:
            resource.current -= number
            if resource.current > resource.max:
                resource.current = resource.max
            ctx.session.commit()
            await ctx.send('{} used {} {}, {}/{} remaining'.format(
                str(character), number, resource.name,
                resource.current, resource.max))
        else:
            await ctx.send('{} does not have enough to use: {}'.format(
                str(character), str(resource)))

    @group.command()
    async def set(self, ctx, name: str, uses: int_or_max):
        '''
        Sets the remaining uses of a resource

        Parameters:
        [name] the name of the resource
        [uses] can be the number of remaining uses or
            the special value "max" to refill all uses
        '''
        character = get_character(ctx.session, ctx.author.id, ctx.guild.id)

        try:
            resource = ctx.session.query(m.Resource)\
                .filter_by(name=name, character=character).one()
        except NoResultFound:
            raise ItemNotFoundError

        if uses == 'max':
            resource.current = resource.max
        else:
            resource.current = uses
        ctx.session.commit()

        await ctx.send('{} now has {}/{} uses of {}'.format(
            str(character), resource.current, resource.max, resource.name))

    @group.command()
    async def check(self, ctx, *, name: str):
        '''
        Checks the status of a resource

        Parameters:
        [name] the name of the resource
        '''
        character = get_character(ctx.session, ctx.author.id, ctx.guild.id)
        try:
            resource = ctx.session.query(m.Resource)\
                .filter_by(name=name, character=character).one()
        except NoResultFound:
            raise ItemNotFoundError
        await ctx.send(str(resource))

    @group.command()
    async def list(self, ctx):
        '''
        Lists all resources for the user
        '''
        character = get_character(ctx.session, ctx.author.id, ctx.guild.id)
        text = ["{}'s resources:".format(character)]
        for resource in character.resources:
            text.append(str(resource))
        await ctx.send('\n'.join(text))

    @group.command(aliases=['delete'])
    async def remove(self, ctx, *, name: str):
        '''
        Deletes a resource from the character

        Parameters:
        [name] the name of the resource
        '''
        character = get_character(ctx.session, ctx.author.id, ctx.guild.id)

        try:
            resource = ctx.session.query(m.Resource)\
                .filter_by(name=name, character=character).one()
        except NoResultFound:
            raise ItemNotFoundError

        ctx.session.delete(resource)
        ctx.session.commit()
        await ctx.send('{} removed'.format(str(resource)))


def setup(bot):
    bot.add_cog(ResourceCog(bot))

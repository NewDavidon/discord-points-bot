import discord

async def update_user_roles(guild, member, points, config):
    """
    Actualiza los roles de un usuario basado en sus puntos.
    """
    if member.bot:  # Ignorar bots
        return

    roles_config = config["roles"]

    # Determinar el rol correcto basado en los puntos
    new_role = None
    if points >= roles_config["max_points"]:
        new_role = discord.utils.get(guild.roles, id=roles_config["max"])
    elif points >= roles_config["medium_points"]:
        new_role = discord.utils.get(guild.roles, id=roles_config["medium"])
    else:
        new_role = discord.utils.get(guild.roles, id=roles_config["base"])

    # Si ya tiene el rol correcto, no hagas nada
    if new_role in member.roles:
        return

    # Remover roles antiguos y asignar el nuevo rol
    for role_id in [roles_config["base"], roles_config["medium"], roles_config["max"]]:
        role = discord.utils.get(guild.roles, id=role_id)
        if role in member.roles:
            await member.remove_roles(role)

    if new_role:
        await member.add_roles(new_role)

async def reward_user(member, points, config, notify_channel=None):
    """
    Recompensa a un usuario si alcanza hitos de puntos.
    """
    if member.bot:  # Ignorar bots
        return

    rewards = config.get("rewards", [])
    for reward in rewards:
        if points >= reward["points"]:
            role = discord.utils.get(member.guild.roles, id=reward["role_id"])
            if role and role not in member.roles:
                await member.add_roles(role)
                if notify_channel:
                    await notify_channel.send(f"🎉 {member.mention}, ¡has recibido el rol {role.name} por alcanzar {reward['points']} puntos!")

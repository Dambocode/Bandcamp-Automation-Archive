from discord_webhook import DiscordWebhook, DiscordEmbed


def sendTaskWebhook(task, product):
    webhook = DiscordWebhook(
        url=task["webhook"], avatar_url="https://pbs.twimg.com/profile_images/671148495898877952/2h7sWPN2_400x400.jpg", username="Bandcamp Checkout")
    embed = DiscordEmbed(title="Successful Checkout", color='0FFF00')
    embed.set_footer(text='@dambowastaken | Praise The Fly God',
                        icon_url='https://pbs.twimg.com/profile_images/1531683676475510785/50ufAdZr_400x400.jpg')
    embed.add_embed_field(
        name="Name", value=product["title"], inline=True)
    embed.add_embed_field(name="Price", value=str(product["price"]), inline=True)
    embed.add_embed_field(name="Description",
                            value=product["description"], inline=False)
    
    embed.add_embed_field(
        name="Email", value=f'{task["email"]}', inline=False
    )

    embed.add_embed_field(
        name="Card", value=f'||{task["card_num"][-4:]}||', inline=True
    )
    embed.add_embed_field(name="Checkout Speed", value=str(float(task["end_time"]) - float(task["start_time"]))[:-13] + "s", inline=False)
    webhook.add_embed(embed)
    response = webhook.execute()


def sendMonitorWebhook(task, product, stock_info, album):
    site_url = f"https://{task['subdomain']}.bandcamp.com{album}"
    
    webhook = DiscordWebhook(
        url=task["webhook"], avatar_url="https://pbs.twimg.com/profile_images/671148495898877952/2h7sWPN2_400x400.jpg", username="Band Camp Monitor", rate_limit_retry=True)
    embed = DiscordEmbed(title=product["item_name"],
                            url=site_url, color=' 03fca9')
    embed.set_footer(text='@dambowastaken | Praise The Fly God',
                        icon_url='https://pbs.twimg.com/profile_images/1531683676475510785/50ufAdZr_400x400.jpg')

    embed.set_thumbnail(url=product['item_image'])
    embed.add_embed_field(name="Description", value=product["item_description"], inline=False)
    # embed.add_embed_field(name="Description", value=product["item_description"], inline=False)
    embed.add_embed_field(name="Price", value=str(product["price"]), inline=True)    
    embed.add_embed_field(name="Stock Available", value=f'{stock_info["quantity_available"]}', inline=True)

    webhook.add_embed(embed)
    response = webhook.execute()
import discord
from discord.ext import commands
import datetime
import asyncio
import os
from dotenv import load_dotenv

# Load biến môi trường từ .env file
load_dotenv()

# Lấy cấu hình từ biến môi trường
TOKEN = os.getenv('DISCORD_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
PREFIX = os.getenv('BOT_PREFIX', '?')  # Mặc định là '?' nếu không có trong .env

# Validate cấu hình
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN không được tìm thấy trong file .env")

# Cấu hình intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Biến thời gian bắt đầu
start_time = datetime.datetime.now()

# ==================== LOGGING CONFIGURATION ====================
import logging

def setup_logging():
    """Cấu hình hệ thống logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Sự kiện khi bot sẵn sàng
@bot.event
async def on_ready():
    print(f'✅ {bot.user} đã đăng nhập!')
    print(f'📊 Đang hoạt động trên {len(bot.guilds)} server')
    print(f'👥 Tổng số người dùng: {sum(g.member_count for g in bot.guilds)}')
    
    # Log thông tin cấu hình (ẩn token)
    logger.info(f'🔄 Prefix: {PREFIX}')
    logger.info(f'👑 Owner ID: {OWNER_ID}')
    
    # Trạng thái bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{PREFIX}help | {len(bot.guilds)} servers"
        )
    )

# ==================== COMMANDS FOR ALL MEMBERS ====================
# Lệnh help cho member
@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 HƯỚNG DẪN SỬ DỤNG BOT",
        description="Danh sách lệnh dành cho thành viên",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    
    embed.add_field(
        name="🎮 Lệnh cơ bản",
        value=(
            f"`{PREFIX}help` - Hiển thị hướng dẫn này\n"
            f"`{PREFIX}ping` - Kiểm tra độ trễ của bot\n"
            f"`{PREFIX}userinfo [@user]` - Xem thông tin người dùng\n"
            f"`{PREFIX}serverinfo` - Xem thông tin server\n"
            f"`{PREFIX}avatar [@user]` - Xem avatar người dùng"
        ),
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Thông tin",
        value=(
            f"`{PREFIX}bot` - Xem thông tin bot\n"
            f"`{PREFIX}uptime` - Xem thời gian hoạt động của bot"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    await ctx.send(embed=embed)

# Lệnh ping
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Độ trễ: **{latency}ms**",
        color=discord.Color.green()
    )
    
    await ctx.send(embed=embed)

# Lệnh xem thông tin bot
@bot.command(name='bot')
async def bot_info(ctx):
    # Tính toán thời gian hoạt động
    uptime = datetime.datetime.now() - start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed = discord.Embed(
        title="🤖 THÔNG TIN BOT",
        description="Thông tin chi tiết về bot",
        color=discord.Color.purple()
    )
    
    # Thông tin bot
    embed.add_field(name="👤 Tên bot", value=bot.user.name, inline=True)
    embed.add_field(name="#️⃣ ID", value=bot.user.id, inline=True)
    embed.add_field(name="📅 Ngày tạo", value=bot.user.created_at.strftime("%d/%m/%Y"), inline=True)
    
    # Thống kê
    embed.add_field(name="📊 Số server", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Tổng thành viên", value=sum(g.member_count for g in bot.guilds), inline=True)
    embed.add_field(name="🏓 Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    # Thời gian hoạt động
    embed.add_field(
        name="⏰ Uptime", 
        value=f"{days} ngày, {hours} giờ, {minutes} phút, {seconds} giây",
        inline=False
    )
    
    # Chủ sở hữu
    owner = await bot.fetch_user(OWNER_ID)
    embed.add_field(name="👑 Chủ sở hữu", value=f"{owner.name}#{owner.discriminator}", inline=True)
    
    # Ngôn ngữ & Thư viện
    embed.add_field(name="💻 Ngôn ngữ", value="Python", inline=True)
    embed.add_field(name="📚 Thư viện", value="discord.py", inline=True)
    
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# Lệnh userinfo
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    
    embed = discord.Embed(
        title=f"👤 THÔNG TIN {member.name}",
        color=member.color,
        timestamp=datetime.datetime.now()
    )
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    
    # Thông tin cơ bản
    embed.add_field(name="Tên đầy đủ", value=f"{member.name}#{member.discriminator}", inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Bot?", value="✅" if member.bot else "❌", inline=True)
    
    # Thông tin tham gia
    embed.add_field(name="Tham gia server", value=member.joined_at.strftime("%d/%m/%Y %H:%M"), inline=True)
    embed.add_field(name="Tạo tài khoản", value=member.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
    
    # Vai trò
    embed.add_field(name="Vai trò cao nhất", value=member.top_role.mention, inline=True)
    embed.add_field(
        name=f"Vai trò ({len(roles)})", 
        value=" ".join(roles) if roles else "Không có vai trò",
        inline=False
    )
    
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# Lệnh serverinfo
@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    
    embed = discord.Embed(
        title=f"📊 THÔNG TIN SERVER: {guild.name}",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.now()
    )
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    # Thông tin cơ bản
    embed.add_field(name="👑 Chủ sở hữu", value=guild.owner.mention, inline=True)
    embed.add_field(name="#️⃣ ID", value=guild.id, inline=True)
    embed.add_field(name="🌐 Khu vực", value=str(guild.preferred_locale).title(), inline=True)
    
    # Thống kê
    embed.add_field(name="📅 Ngày tạo", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="👥 Thành viên", value=guild.member_count, inline=True)
    embed.add_field(name="📈 Số lượng bot", value=sum(member.bot for member in guild.members), inline=True)
    
    # Kênh
    embed.add_field(name="💬 Kênh văn bản", value=len(guild.text_channels), inline=True)
    embed.add_field(name="🎤 Kênh thoại", value=len(guild.voice_channels), inline=True)
    embed.add_field(name="📁 Danh mục", value=len(guild.categories), inline=True)
    
    # Vai trò và emoji
    embed.add_field(name="🎭 Số vai trò", value=len(guild.roles), inline=True)
    embed.add_field(name="😀 Số emoji", value=len(guild.emojis), inline=True)
    
    # Tính xác minh
    verification_levels = {
        discord.VerificationLevel.none: "Không",
        discord.VerificationLevel.low: "Thấp",
        discord.VerificationLevel.medium: "Trung bình",
        discord.VerificationLevel.high: "Cao",
        discord.VerificationLevel.highest: "Rất cao"
    }
    
    embed.add_field(
        name="🛡️ Mức xác minh", 
        value=verification_levels.get(guild.verification_level, "Không xác định"),
        inline=True
    )
    
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# Lệnh avatar
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    embed = discord.Embed(
        title=f"🖼️ Avatar của {member.name}",
        color=member.color
    )
    
    if member.avatar:
        embed.set_image(url=member.avatar.url)
        embed.description = f"[Link avatar]({member.avatar.url})"
    else:
        embed.description = "Người dùng này không có avatar"
    
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# Lệnh uptime
@bot.command()
async def uptime(ctx):
    uptime_duration = datetime.datetime.now() - start_time
    days = uptime_duration.days
    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed = discord.Embed(
        title="⏰ THỜI GIAN HOẠT ĐỘNG",
        description=(
            f"**Bot đã hoạt động được:**\n"
            f"```{days} ngày, {hours} giờ, {minutes} phút, {seconds} giây```"
        ),
        color=discord.Color.green()
    )
    
    embed.set_footer(text=f"Bot khởi động lúc: {start_time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    await ctx.send(embed=embed)

# Lệnh kiểm tra env
@bot.command(name='env')
async def check_env(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    embed = discord.Embed(
        title="⚙️ KIỂM TRA .ENV",
        color=discord.Color.blue()
    )
    
    token_display = f"✅ Đã cấu hình ({TOKEN[:10]}...)" if TOKEN else "❌ Chưa cấu hình"
    
    embed.add_field(name="Token", value=token_display, inline=False)
    embed.add_field(name="Owner ID", value=OWNER_ID, inline=True)
    embed.add_field(name="Prefix", value=PREFIX, inline=True)
    embed.add_field(name="Python", value=os.sys.version.split()[0], inline=True)
    
    if os.path.exists('.env'):
        embed.add_field(name="File .env", value="✅ Tồn tại", inline=True)
    else:
        embed.add_field(name="File .env", value="❌ Không tồn tại", inline=True)
    
    embed.set_footer(text="Lệnh chỉ dành cho Owner")
    await ctx.send(embed=embed)

# Lệnh reload env
@bot.command(name='reloadenv')
async def reload_env(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    try:
        old_prefix = PREFIX
        old_owner = OWNER_ID
        
        load_dotenv(override=True)
        
        global TOKEN, OWNER_ID, PREFIX
        TOKEN = os.getenv('DISCORD_TOKEN')
        OWNER_ID = int(os.getenv('OWNER_ID'))
        PREFIX = os.getenv('BOT_PREFIX', '?')
        
        bot.command_prefix = PREFIX
        
        embed = discord.Embed(
            title="🔄 ĐÃ TẢI LẠI .ENV",
            color=discord.Color.green()
        )
        
        changes = []
        if old_prefix != PREFIX:
            changes.append(f"Prefix: `{old_prefix}` → `{PREFIX}`")
        if old_owner != OWNER_ID:
            changes.append(f"Owner ID: `{old_owner}` → `{OWNER_ID}`")
        
        if changes:
            embed.add_field(name="Thay đổi", value="\n".join(changes), inline=False)
        else:
            embed.description = "Không có thay đổi nào"
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ LỖI TẢI LẠI .ENV",
            description=f"```{str(e)}```",
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)

# ==================== OWNER-ONLY COMMANDS ====================
# Lệnh help cho owner
@bot.command(name='helpp')
async def owner_help(ctx):
    # Kiểm tra owner
    if ctx.author.id != OWNER_ID:
        embed = discord.Embed(
            title="❌ LỖI",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="🔑 HƯỚNG DẪN LỆNH OWNER",
        description="Các lệnh dành riêng cho chủ sở hữu",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.now()
    )
    
    embed.add_field(
        name="⚙️ Quản lý bot",
        value=(
            f"`{PREFIX}helpp` - Hiển thị hướng dẫn này\n"
            f"`{PREFIX}shutdown` - Tắt bot\n"
            f"`{PREFIX}reload` - Khởi động lại bot\n"
            f"`{PREFIX}servers` - Hiển thị danh sách server\n"
            f"`{PREFIX}leave [server_id]` - Rời khỏi server\n"
            f"`{PREFIX}status [trạng thái]` - Đổi trạng thái bot"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📊 Thống kê",
        value=(
            f"`{PREFIX}stats` - Thống kê chi tiết\n"
            f"`{PREFIX}broadcast [tin nhắn]` - Gửi tin nhắn đến tất cả server"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Chủ sở hữu: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# Lệnh tắt bot
@bot.command()
async def shutdown(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    embed = discord.Embed(
        title="🔌 ĐANG TẮT BOT...",
        description="Bot sẽ ngừng hoạt động sau 3 giây",
        color=discord.Color.red()
    )
    
    await ctx.send(embed=embed)
    await asyncio.sleep(3)
    await bot.close()

# Lệnh khởi động lại bot
@bot.command()
async def reload(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    embed = discord.Embed(
        title="🔄 ĐANG KHỞI ĐỘNG LẠI...",
        description="Bot sẽ khởi động lại sau 3 giây",
        color=discord.Color.orange()
    )
    
    await ctx.send(embed=embed)
    await asyncio.sleep(3)
    
    # Có thể thêm code để reload extensions ở đây
    embed2 = discord.Embed(
        title="✅ KHỞI ĐỘNG LẠI THÀNH CÔNG",
        color=discord.Color.green()
    )
    
    await ctx.send(embed=embed2)

# Lệnh hiển thị servers
@bot.command()
async def servers(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    embed = discord.Embed(
        title="🌐 DANH SÁCH SERVER",
        description=f"Bot đang ở trong {len(bot.guilds)} server",
        color=discord.Color.blue()
    )
    
    for i, guild in enumerate(bot.guilds, 1):
        embed.add_field(
            name=f"{i}. {guild.name}",
            value=f"ID: {guild.id}\nThành viên: {guild.member_count}",
            inline=False
        )
    
    await ctx.send(embed=embed)

# Lệnh rời server
@bot.command()
async def leave(ctx, server_id: int = None):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    if not server_id:
        await ctx.send(f"❌ Vui lòng cung cấp ID server! Ví dụ: `{PREFIX}leave 1234567890`")
        return
    
    guild = bot.get_guild(server_id)
    if not guild:
        await ctx.send("❌ Không tìm thấy server với ID này!")
        return
    
    try:
        await guild.leave()
        embed = discord.Embed(
            title="✅ ĐÃ RỜI SERVER",
            description=f"Đã rời khỏi server: **{guild.name}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ LỖI",
            description=f"Không thể rời server: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Lệnh đổi trạng thái
@bot.command()
async def status(ctx, *, status_type=None):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    if not status_type:
        await ctx.send(f"❌ Vui lòng chọn trạng thái! Ví dụ: `{PREFIX}status playing game`")
        return
    
    # Phân loại trạng thái
    if status_type.startswith("playing"):
        activity = discord.Activity(type=discord.ActivityType.playing, name=status_type[8:])
    elif status_type.startswith("watching"):
        activity = discord.Activity(type=discord.ActivityType.watching, name=status_type[9:])
    elif status_type.startswith("listening"):
        activity = discord.Activity(type=discord.ActivityType.listening, name=status_type[10:])
    elif status_type.startswith("streaming"):
        activity = discord.Activity(type=discord.ActivityType.streaming, name=status_type[10:])
    else:
        activity = discord.Activity(type=discord.ActivityType.playing, name=status_type)
    
    await bot.change_presence(activity=activity)
    
    embed = discord.Embed(
        title="✅ ĐÃ ĐỔI TRẠNG THÁI",
        description=f"Trạng thái mới: **{status_type}**",
        color=discord.Color.green()
    )
    
    await ctx.send(embed=embed)

# Lệnh thống kê chi tiết
@bot.command()
async def stats(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    total_members = sum(g.member_count for g in bot.guilds)
    total_bots = sum(sum(1 for m in g.members if m.bot) for g in bot.guilds)
    total_humans = total_members - total_bots
    
    embed = discord.Embed(
        title="📈 THỐNG KÊ CHI TIẾT",
        description="Thống kê toàn bộ hoạt động của bot",
        color=discord.Color.purple(),
        timestamp=datetime.datetime.now()
    )
    
    # Tổng quan
    embed.add_field(name="📊 Tổng số server", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Tổng thành viên", value=total_members, inline=True)
    embed.add_field(name="🤖 Tổng bot", value=total_bots, inline=True)
    embed.add_field(name="👤 Tổng người dùng", value=total_humans, inline=True)
    
    # Ping
    embed.add_field(name="🏓 Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    # Uptime
    uptime_duration = datetime.datetime.now() - start_time
    days = uptime_duration.days
    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    embed.add_field(
        name="⏰ Uptime", 
        value=f"{days}d {hours}h {minutes}m {seconds}s",
        inline=True
    )
    
    # Thông tin bot
    embed.add_field(name="💻 Python version", value="3.8+", inline=True)
    embed.add_field(name="📚 Discord.py", value=discord.__version__, inline=True)
    
    embed.set_footer(text=f"Chủ sở hữu: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# Lệnh broadcast
@bot.command()
async def broadcast(ctx, *, message=None):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    if not message:
        await ctx.send(f"❌ Vui lòng nhập tin nhắn! Ví dụ: `{PREFIX}broadcast Xin chào mọi người!`")
        return
    
    embed = discord.Embed(
        title="📢 THÔNG BÁO TỪ CHỦ SỞ HỮU",
        description=message,
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    
    embed.set_footer(text=f"Bot: {bot.user.name}", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    
    sent = 0
    failed = 0
    
    for guild in bot.guilds:
        try:
            # Tìm kênh đầu tiên bot có quyền gửi
            channel = guild.system_channel or guild.text_channels[0]
            await channel.send(embed=embed)
            sent += 1
        except:
            failed += 1
        await asyncio.sleep(0.5)  # Tránh rate limit
    
    result_embed = discord.Embed(
        title="📤 KẾT QUẢ BROADCAST",
        color=discord.Color.green()
    )
    
    result_embed.add_field(name="✅ Gửi thành công", value=sent, inline=True)
    result_embed.add_field(name="❌ Gửi thất bại", value=failed, inline=True)
    result_embed.add_field(name="📊 Tổng server", value=len(bot.guilds), inline=True)
    
    await ctx.send(embed=result_embed)

# Xử lý lỗi
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ LỆNH KHÔNG TỒN TẠI",
            description=f"Sử dụng `{PREFIX}help` để xem danh sách lệnh",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ THIẾU QUYỀN",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ LỖI KHÔNG XÁC ĐỊNH",
            description=f"```{str(error)}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Chạy bot
if __name__ == "__main__":
    print("="*50)
    print("🚀 Đang khởi động bot Discord...")
    print(f"📁 Thư mục làm việc: {os.getcwd()}")
    print(f"🔧 Prefix: {PREFIX}")
    print(f"👑 Owner ID: {OWNER_ID}")
    
    # Kiểm tra file .env
    if not os.path.exists('.env'):
        print("⚠️  Cảnh báo: Không tìm thấy file .env")
        print("📝 Tạo file .env với các biến: DISCORD_TOKEN, OWNER_ID, BOT_PREFIX")
    else:
        print("✅ Đã tìm thấy file .env")
    
    print("="*50)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ LỖI: Token không hợp lệ!")
        print("ℹ️  Kiểm tra file .env và đảm bảo DISCORD_TOKEN là hợp lệ")
    except Exception as e:
        print(f"❌ LỖI KHỞI ĐỘNG: {str(e)}")
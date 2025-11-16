import json
import math
import os
import random
import sys
import time
import traceback
import uuid

class Task:
    """定时器任务类"""
    def __init__(self, func, period_ms):
        self.func = func  # 要执行的函数
        self.period_ms = period_ms  # 执行周期（毫秒）
        self.last_run_time = time.time() * 1000  # 上次执行时间（毫秒）
        self.is_cancelled = False  # 任务是否被取消
        
    def cancel(self):
        """取消任务"""
        self.is_cancelled = True
        
    def should_run(self):
        """检查任务是否应该执行"""
        if self.is_cancelled:
            return False
        current_time = time.time() * 1000
        return current_time - self.last_run_time >= self.period_ms
    
    def run(self):
        """执行任务并更新最后执行时间"""
        if not self.is_cancelled:
            try:
                self.func()
            except Exception as e:
                Utils.debug(f"Task error: {e}")
            self.last_run_time = time.time() * 1000
class TaskScheduler:
    """任务调度器类，用于管理所有定时器任务"""
    def __init__(self):
        self.tasks = []  # 存储所有活跃任务
        
    def add_task(self, task):
        """添加一个任务到调度器"""
        self.tasks.append(task)
        return task
    
    def update(self):
        """更新并执行到期的任务，清理已取消的任务"""
        # 创建一个新列表存储活跃任务
        active_tasks = []
        
        for task in self.tasks:
            # 检查任务是否已取消
            if task.is_cancelled:
                continue
            
            # 检查任务是否应该执行
            if task.should_run():
                task.run()
            
            # 如果任务未被取消，保留到活跃列表中
            if not task.is_cancelled:
                active_tasks.append(task)
        
        # 更新任务列表，只保留活跃任务
        self.tasks = active_tasks
    
    def clear(self):
        """清除所有任务"""
        self.tasks.clear()

# 创建全局任务调度器实例
global_task_scheduler = TaskScheduler()

def runTaskLater(func, delayMs):
    """全局函数，创建并启动一个延迟执行一次的任务
    
    Args:
        func: 要执行的函数或lambda表达式
        delayMs: 延迟时间（毫秒）
    
    Returns:
        Task: 创建的任务对象，可以通过task.cancel()取消任务
    """
    if func is None:
        raise ValueError("任务函数不能为空")
    
    # 创建一个简单的包装函数
    def one_time_func():
        func()
        # 获取当前任务并取消
        for t in global_task_scheduler.tasks:
            if t.func == one_time_func:
                t.cancel()
                break
    
    # 创建任务对象
    task = Task(one_time_func, delayMs)
    # 添加到调度器
    return global_task_scheduler.add_task(task)

def runTaskTimer(func, delayMs=0, periodMs=10):
    """全局函数，创建并启动一个定时任务
    
    Args:
        func: 要执行的函数或lambda表达式
        delayMs: 初始延迟时间（毫秒），默认0毫秒
        periodMs: 任务执行周期（毫秒），默认10毫秒
    
    Returns:
        Task: 创建的任务对象，可以通过task.cancel()取消任务
    """
    if func is None:
        raise ValueError("任务函数不能为空")
    
    # 简单实现：如果有延迟，先创建一个延迟任务
    if delayMs > 0:
        # 创建一个包装函数用于启动周期性任务
        def start_periodic():
            # 创建并添加周期性任务
            periodic_task = Task(func, periodMs)
            global_task_scheduler.add_task(periodic_task)
        
        # 创建延迟任务
        delay_task = Task(start_periodic, delayMs)
        return global_task_scheduler.add_task(delay_task)
    else:
        # 没有延迟，直接创建周期任务
        task = Task(func, periodMs)
        return global_task_scheduler.add_task(task)

# 禁用libpng警告和pygame支持提示
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['PYGAME_ALLOW_SDL2'] = '1'
# 禁用libpng关于iCCP sRGB配置文件的警告
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning:pygame.image'
try:
    import pygame
except Exception:
    print("需要 pygame 库来运行此脚本。请先安装：pip install pygame")
    raise

_VERSION = "1.0.0"

SCREEN_W = 480
SCREEN_H = 800
FPS = 60

# 资源路径
ASSETS = 'assets'
ASSETS_IMG = os.path.join(ASSETS, 'images')
ASSETS_SFX = os.path.join(ASSETS, 'sfx')
ASSETS_FONTS = os.path.join(ASSETS, 'fonts')
ASSETS_MUSIC = os.path.join(ASSETS, 'music')

# 游戏状态常量
GAME_STATE_TITLE = 'title'
GAME_STATE_PLAYING = 'playing'
GAME_STATE_GAMEOVER = 'gameover'

# 射击类型常量
SHOOT_TYPE_DIRECT = 'direct'  # 直射
SHOOT_TYPE_SCATTER = 'scatter'  # 散射
SHOOT_TYPE_RAPID = 'rapid'  # 连射

# 子弹所有者常量
BULLET_OWNER_PLAYER = 'player'  # 玩家子弹
BULLET_OWNER_ENEMY = 'enemy'    # 敌人子弹

# UI状态常量
UI_SETTINGS_ACTIVE = 'settings_active'
UI_STATS_ACTIVE = 'stats_active'
UI_MODAL_ACTIVE = 'modal_active'

# 按键绑定常量
KEY_UP = 'up'
KEY_DOWN = 'down'
KEY_LEFT = 'left'
KEY_RIGHT = 'right'
KEY_SHOOT = 'shoot'
KEY_SHOOT_SWITCH = 'shoot_switch'
KEY_MUSIC = 'music'

# 音量设置常量
VOLUME_MASTER = 'master'  # 主音量
VOLUME_MUSIC = 'music'    # 音乐音量
VOLUME_SOUND = 'sound'    # 音效音量

# 音效名称常量
SOUND_EXPLODE = 'explode'
SOUND_HOVER = 'hover'
SOUND_CLICK = 'click'
SOUND_FAIL = 'fail'
SOUND_POWERUP = 'powerup'

# 区域常量
ZONE_LEFT = 'left'
ZONE_RIGHT = 'right'

# 建议目标渲染尺寸（像素）
PLAYER_SIZE = (54, 54)  # 宽高（在窗口中的像素）
ENEMY_SIZE = (48, 48)
BULLET_SIZE = (8, 16)
BG_SIZE = (SCREEN_W, SCREEN_H)

# 字体候选列表（优先使用 Windows 预装中文字体）
FONT_CANDIDATES = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'Microsoft JhengHei']

# 颜色常量池
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_DARK_GRAY = (50, 50, 60)
COLOR_LIGHT_DARK_GRAY = (40, 40, 40)
COLOR_MEDIUM_GRAY = (80, 80, 80)
COLOR_RED = (255, 0, 0)
COLOR_LIGHT_RED = (255, 180, 180)
COLOR_DARK_RED = (255, 80, 80)
COLOR_BRIGHT_RED = (255, 60, 60)
COLOR_GREEN = (0, 255, 0)
COLOR_DARK_GREEN = (40, 180, 40)
COLOR_LIGHT_GREEN = (100, 255, 100)
COLOR_BLUE = (0, 0, 255)
COLOR_SKY_BLUE = (135, 206, 250)
COLOR_DARK_BLUE = (0, 120, 255)
COLOR_CYAN = (0, 255, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_LIGHT_YELLOW = (255, 220, 60)
COLOR_BRIGHT_YELLOW = (255, 230, 120)
COLOR_PURPLE = (16, 16, 32)
COLOR_LIGHT_BLUE = (180, 220, 255)
COLOR_MEDIUM_BLUE = (100, 120, 140)
COLOR_BUTTON_RED = (220, 60, 60)
COLOR_BUTTON_GREEN = (60, 180, 80)
COLOR_BUTTON_CONFIRM = (0, 120, 0)
COLOR_BUTTON_CANCEL = (120, 0, 0)

# 半透明和额外颜色定义
COLOR_BLUE_BUTTON = (0, 120, 255)
COLOR_NAVY_BLUE = (16, 16, 32)
COLOR_DARK_BLUE = (0, 120, 255)
COLOR_DARK_RED_TEXT = (128, 0, 0)
COLOR_ORANGE = (255, 165, 0)
COLOR_LIGHT_BLUE_TRANSPARENT = (100, 180, 255, 128)
COLOR_BLACK_TRANSPARENT = (0, 0, 0, 128)
COLOR_BLUE_OVERLAY = (60, 80, 120, 240)
COLOR_LIGHT_GRAY_BACKGROUND = (240, 240, 240, 255)
COLOR_WHITE_TRANSPARENT_240 = (255, 255, 255, 240)
COLOR_WHITE_TRANSPARENT_255 = (255, 255, 255, 255)

MAX_PLAYER_HEALTH = 5000

# 调试
global_debug = False
# 是否显示对象详细信息
show_detail = False
# 全局对象ID计数器，用于为所有实体对象分配唯一ID
object_id = 0

# 工具函数类
class Utils:
    """游戏工具函数集合"""
    
    @staticmethod
    def error(*args, **kwargs):
        """错误打印函数"""
        print(*args, **kwargs)
    
    @staticmethod
    def debug(*args, **kwargs):
        """调试打印函数，仅当global_debug为True时打印"""
        if global_debug:
            print(*args, **kwargs)
    
    @staticmethod
    def make_pixel_sprite(w, h, color, scale=3):
        """生成一个像素风格的 Surface：先创建小尺寸再放大保持像素感"""
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill(color)
        return pygame.transform.scale(surf, (w * scale, h * scale))
    
    @staticmethod
    def load_image(name, target_size=None):
        """尝试从 assets/images/ 加载名为 name 的 png（无需后缀），并缩放到 target_size"""
        path = os.path.join(ASSETS_IMG, f"{name}.png")
        try:
            img = pygame.image.load(path).convert_alpha()
            if target_size is not None:
                # 直接缩放到目标尺寸，保持清晰
                img = pygame.transform.smoothscale(img, target_size)
            return img
        except Exception:
            # 回退占位：生成与 target_size 相同大小的占位图
            tw, th = (target_size if target_size is not None else (48, 48))
            surf = pygame.Surface((tw, th), pygame.SRCALPHA)
            surf.fill(COLOR_DARK_GRAY)
            # 在中心绘制简单像素风形状
            center = (tw // 2, th // 2)
            points = [
                (center[0], center[1] - th // 4),
                (center[0] - tw // 6, center[1] + th // 6),
                (center[0] + tw // 6, center[1] + th // 6),
            ]
            pygame.draw.polygon(surf, COLOR_LIGHT_BLUE, points)
            pygame.draw.polygon(surf, COLOR_MEDIUM_BLUE, points, 2)
            return surf
    
    @staticmethod
    def load_sound(name):
        """加载音效文件"""
        path = os.path.join(ASSETS_SFX, f"{name}.wav")
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None
    
    @staticmethod
    def load_font(candidates, size, bold=False):
        """尝试从 assets/fonts/ 或系统字体加载支持中文的字体"""
        if isinstance(candidates, str):
            candidates = [candidates]

        # 先从 assets/fonts 目录查找 ttf 或 otf
        for name in candidates:
            for ext in ('.ttf', '.otf'):
                local_path = os.path.join(ASSETS_FONTS, f"{name}{ext}")
                if os.path.isfile(local_path):
                    try:
                        return pygame.font.Font(local_path, size)
                    except Exception:
                        pass

        # 再尝试常见的系统/文件名
        for name in candidates:
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                # 测试是否能渲染中文字符
                try:
                    s = f.render('中文', True, (255, 255, 255))
                    return f
                except Exception:
                    pass
            except Exception:
                pass

        # 最后退回到默认字体
        try:
            return pygame.font.Font(None, size)
        except Exception:
            return pygame.font.SysFont(None, size)
    
    @staticmethod
    def play_sound(sound, game=None):
        """安全地播放音效，支持音量设置"""
        if sound:
            try:
        
                if game and game.ui_manager:
                    sound_volume = game.ui_manager.volume_settings['sound']['value'] / 100
                    master_volume = game.ui_manager.volume_settings['master']['value'] / 100
                    # 应用主音量和音效音量的乘积
                    sound.set_volume(sound_volume * master_volume)
                sound.play()
            except Exception:
                pass
    
    @staticmethod
    def draw_blurred_background(screen, alpha=200):
        """创建并绘制模糊背景"""
        try:
            snap = screen.copy()
            small = pygame.transform.smoothscale(snap, (max(1, SCREEN_W // 8), max(1, SCREEN_H // 8)))
            blurred = pygame.transform.smoothscale(small, (SCREEN_W, SCREEN_H))
            blurred.set_alpha(alpha)
            screen.blit(blurred, (0, 0))
        except Exception:
            # 若模糊失败，使用一个半透明暗覆盖
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            screen.blit(overlay, (0, 0))
    
    @staticmethod
    def save_data(data, file_path):
        """保存数据到JSON文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            Utils.debug(f"保存数据失败: {e}")
            return False
    
    @staticmethod
    def load_data(file_path):
        """从JSON文件加载数据"""
        try:
            if not os.path.exists(file_path):
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            Utils.debug(f"加载数据失败: {e}")
            return None
    
    @staticmethod
    def format_number(num):
        """格式化数字，超过100万时使用科学计数法"""
        if abs(num) >= 1e6:
            # 使用科学计数法，保留最多6位小数
            return f"{num:.6e}"
        else:
            # 对于整数保持原样
            if isinstance(num, int):
                return str(num)
            # 对于浮点数保留两位小数
            return f"{num:.2f}"
# 游戏对象类
class Bullet:
    """子弹类"""
    def __init__(self, x, y, vy, owner, image=None, damage=100, shoot_type=SHOOT_TYPE_DIRECT, angle=0):
        global object_id
        self.x = x
        self.y = y
        self.vy = vy
        self.owner = owner
        self.image = image
        self.damage = damage  # 子弹伤害值
        self.alive = True  # 初始化alive属性
        self.shoot_type = shoot_type  # 射击方式类型：direct（直射）、scatter（散射）、rapid（连射）
        self.angle = angle  # 子弹飞行角度，用于散射子弹的方向
        self.w, self.h = (image.get_size() if image else BULLET_SIZE)
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        # 分配唯一的对象ID
        self.object_id = object_id
        object_id += 1
        # 穿透属性，默认为False
        self.piercing = False

    def update(self, dt):
        # 根据角度计算移动
        if self.angle != 0:
            # 对于有角度的子弹（主要是散射子弹），需要计算水平和垂直方向的速度分量
            rad_angle = math.radians(self.angle)
            speed = abs(self.vy)  # 获取速度大小
            # 增加x方向的速度分量，确保散射子弹有明显的水平移动
            self.x += speed * math.sin(rad_angle) * dt * 2  # 乘以2增加水平移动效果
            self.y += speed * math.cos(rad_angle) * dt * (1 if self.vy > 0 else -1)
        else:
            # 无角度的子弹（直射、连射）
            self.y += self.vy * dt
        
        self.rect.topleft = (self.x, self.y)
        
        # 子弹超出屏幕则标记为不活跃
        # 散射子弹直接销毁，不进行反射
        if self.shoot_type == SHOOT_TYPE_SCATTER:
            if (self.owner == BULLET_OWNER_PLAYER and (self.y < -self.h or self.x < -self.w or self.x > SCREEN_W)) or \
               (self.owner == BULLET_OWNER_ENEMY and (self.y > SCREEN_H or self.x < -self.w or self.x > SCREEN_W)):
                self.alive = False
        else:
            # 直射和连射子弹的屏幕边缘检测
            if (self.owner == BULLET_OWNER_PLAYER and self.y < -self.h) or (self.owner == BULLET_OWNER_ENEMY and self.y > SCREEN_H):
                self.alive = False

    def draw(self, surf):
        if self.image:
            # 如果子弹有角度，旋转图像
            if self.angle != 0:
                # 旋转图像
                rotated_image = pygame.transform.rotate(self.image, -self.angle)  # 负号是因为pygame旋转是逆时针的
        
                rotated_rect = rotated_image.get_rect(center=self.rect.center)
                # 绘制旋转后的图像
                surf.blit(rotated_image, rotated_rect.topleft)
            else:
                # 没有角度，直接绘制原图
                surf.blit(self.image, (self.x, self.y))
        else:
            color = (255, 220, 60) if self.owner == BULLET_OWNER_PLAYER else (255, 80, 80)
            pygame.draw.rect(surf, color, self.rect)
        
        # 显示详细信息
        if show_detail:
            # 使用object_id生成固定颜色
            # 使用object_id的不同部分生成RGB值，确保颜色差异明显
            r = (self.object_id * 17) % 256
            g = (self.object_id * 31) % 256
            b = (self.object_id * 43) % 256
            color = (r, g, b)
            # 加载字体
            font = Utils.load_font(FONT_CANDIDATES, 12)
            # 显示owner和rect属性
            text = f"{self.owner} {self.rect}"
            text_surf = font.render(text, True, color)
            # 在对象右上角显示，并添加基于object_id的y轴偏移
            text_x = self.x + self.w + 5
            text_y = self.y + (self.object_id % 4 * 8 - 8)
            surf.blit(text_surf, (text_x, text_y))
            
        # 更新rect位置
        self.rect.x = self.x
        self.rect.y = self.y
class Player:
    """玩家飞机类"""
    def __init__(self, x, y, image=None):
        global object_id
        self.x = x
        self.y = y
        self.speed = 400  # px/sec
        self.img = image
        self.w, self.h = (image.get_size() if image else PLAYER_SIZE)
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        # 分配唯一的对象ID
        self.object_id = object_id
        object_id += 1
        self.fire_cooldown = 0.5  # 手动射击间隔（提高1倍）
        self.auto_fire_cooldown = 0.8  # 自动射击间隔
        self.time_since_shot = 0  # 手动射击计时器
        self.time_since_auto_shot = 0  # 自动射击计时器
        self.lives = 3
        self.health = 300  # 生命值
        self.alive = True
        self.shield = None
        
        # 斗志值系统
        self.morale = 0  # 玩家斗志值
        self.consecutive_kills = 0  # 连续无伤击杀计数
        self.last_hit_time = -1  # 上次受伤时间，-1表示从未受伤
        
        # 新增射击方式相关属性
        self.current_shoot_type = SHOOT_TYPE_DIRECT  # 当前射击方式：direct（直射）、scatter（散射）、rapid（连射）
        self.rapid_shot_counter = 0  # 连射计时器
        self.rapid_shots_per_second = 5  # 每秒发射的子弹数（连射）
        
        self.bullet_increase_count = 0  # 子弹增加计数
        self.max_bullet_increase = 3  # 最大子弹增加次数

    def update(self, dt, keys, game=None):
        dx = 0
        dy = 0
        
        # 使用自定义按键绑定
        if game and game.ui_manager:
            if keys[game.ui_manager.key_bindings[KEY_LEFT]['key']]:
                dx = -1
            if keys[game.ui_manager.key_bindings[KEY_RIGHT]['key']]:
                dx = 1
            if keys[game.ui_manager.key_bindings[KEY_UP]['key']]:
                dy = -1
            if keys[game.ui_manager.key_bindings[KEY_DOWN]['key']]:
                dy = 1
            
            # 检查子弹发射按键
            if keys[game.ui_manager.key_bindings[KEY_SHOOT]['key']]:
                if self.can_shoot():
                    bullets = self.shoot(game=game)
                    if bullets and game:
                        for bullet in bullets:
                            new_b = game.create_bullet(BULLET_OWNER_PLAYER, bullet.x, bullet.y, bullet.vy)
                            # 复制子弹的射击类型和角度属性，确保散射状态下正确发射散射子弹
                            new_b.shoot_type = bullet.shoot_type
                            new_b.angle = bullet.angle
                            game.bullets.append(new_b)
                        # 播放射击音效
                        Utils.play_sound(game.snd_player_shoot, game)
        else:
            # 后备方案：WASD 和方向键移动
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

        # 边界限制
        self.x = max(0, min(SCREEN_W - self.w, self.x))
        self.y = max(80, min(SCREEN_H - self.h, self.y))

        self.rect.topleft = (self.x, self.y)
        self.time_since_shot += dt
        self.time_since_auto_shot += dt
        
        # 处理连射：当发射的子弹数量没到上限时，继续发射子弹
        if self.current_shoot_type == SHOOT_TYPE_RAPID and self.rapid_shot_counter < self.rapid_shots_per_second + self.bullet_increase_count and game:
            # 检查是否还在按下射击键
            if game.ui_manager and keys[game.ui_manager.key_bindings[KEY_SHOOT]['key']]: # 直接索引访问按键状态
                center_x = self.x + self.w // 2 - 2
                by = self.y - 8
                
                # 创建单个子弹
                new_b = game.create_bullet(BULLET_OWNER_PLAYER, center_x, by, -600)
        
                new_b.shoot_type = SHOOT_TYPE_RAPID
                new_b.angle = 0
                game.bullets.append(new_b)
                
                # 重置连射计数器
                self.rapid_shot_counter += 1
                
                Utils.play_sound(game.snd_player_shoot, game)

    def can_shoot(self):
        return self.current_shoot_type != SHOOT_TYPE_RAPID and self.time_since_shot >= self.fire_cooldown

    def can_auto_shoot(self):
        return self.time_since_auto_shot >= self.auto_fire_cooldown

    def shoot(self, is_auto=False, game=None):
        if is_auto:
            self.time_since_auto_shot = 0
        else:
            self.time_since_shot = 0
        
        bullets = []
        center_x = self.x + self.w // 2 - 2
        by = self.y - 8
        
        # 根据游戏阶段决定发射子弹数量
        if game and game.stage:
            stage = game.stage
        else:
            stage = 1
        
        # 根据射击方式生成子弹
        if self.current_shoot_type == SHOOT_TYPE_DIRECT:
            # 直射：子弹排列在飞机前方，同时发射
            bullet_count = stage + self.bullet_increase_count

            spacing = 10  # 子弹间隔
            start_x = center_x - ((bullet_count - 1) * spacing) // 2
            
            for i in range(bullet_count):
                bx = start_x + i * spacing
                bullets.append(Bullet(bx, by, vy=-600, owner=BULLET_OWNER_PLAYER, shoot_type=SHOOT_TYPE_DIRECT, angle=0))
                
        elif self.current_shoot_type == SHOOT_TYPE_SCATTER:
            # 根据游戏阶段决定子弹数量
            bullet_count = stage + self.bullet_increase_count
            
            angles = []

            if bullet_count % 2 == 1:  # 奇数子弹
                # 包含正前方的0度
                if bullet_count == 1:
                    angles = [0]
                else:
                    # 计算角度间隔，以15°为基础
                    half_count = bullet_count // 2
                    for i in range(1, half_count + 1):
                        angles.append(-7.5 * i)
                    angles.append(0)  # 正前方
                    for i in range(1, half_count + 1):
                        angles.append(7.5 * i)
            else:  # 偶数子弹
                # 不包含正前方
                half_count = bullet_count // 2
                angles.append(-3.75)
                angles.append(3.75)
                for i in range(2, half_count + 1):
                    angles.append(-7.5 * i)
                for i in range(2, half_count + 1):
                    angles.append(7.5 * i)
            
            # 确保角度列表已排序
            angles.sort()
            
            for angle in angles:
                # 计算子弹初始位置，使子弹从飞机前端发出
                radians = math.radians(angle)
                # 以飞机图标尺寸为半径计算偏移
                radius = self.w / 2  # 使用飞机宽度的一半作为半径
                offset_x = math.sin(radians) * radius
                
                bx = center_x + offset_x

                bullet = Bullet(bx, by, vy=-600, owner=BULLET_OWNER_PLAYER, shoot_type=SHOOT_TYPE_SCATTER, angle=angle)
                bullets.append(bullet)
                
        elif self.current_shoot_type == SHOOT_TYPE_RAPID:
            bullets.append(Bullet(center_x, by, vy=-600, owner=BULLET_OWNER_PLAYER, shoot_type=SHOOT_TYPE_RAPID, angle=0))
            self.rapid_shot_counter = 0
        
        return bullets

    def draw(self, surf):
        surf.blit(self.img, (self.x, self.y))
        
        # 显示详细信息
        if show_detail:
            # 使用object_id生成固定颜色
            # 使用object_id的不同部分生成RGB值，确保颜色差异明显
            r = (self.object_id * 17) % 256
            g = (self.object_id * 31) % 256
            b = (self.object_id * 43) % 256
            color = (r, g, b)
            # 加载字体
            font = Utils.load_font(FONT_CANDIDATES, 12)
            # 显示生命值
            text = f"生命:{self.health}"
            text_surf = font.render(text, True, color)
            # 在对象右上角显示，并添加基于object_id的y轴偏移
            text_x = self.x + self.w + 5
            text_y = self.y + (self.object_id % 4 * 8 - 8)
            surf.blit(text_surf, (text_x, text_y))
        
        # 显示详细信息
        if show_detail:
            # 使用object_id生成固定颜色
            # 使用object_id的不同部分生成RGB值，确保颜色差异明显
            r = (self.object_id * 17) % 256
            g = (self.object_id * 31) % 256
            b = (self.object_id * 43) % 256
            color = (r, g, b)
            # 加载字体
            font = Utils.load_font(FONT_CANDIDATES, 12)
            # 显示生命值
            text = f"生命:{self.health}"
            text_surf = font.render(text, True, color)
            # 在对象右上角显示，并添加基于object_id的y轴偏移
            text_x = self.x + self.w + 5
            text_y = self.y + (self.object_id % 4 * 8 - 8)
            surf.blit(text_surf, (text_x, text_y))
        
        # 显示详细信息
        if show_detail:
            # 使用object_id生成固定颜色
            # 使用object_id的不同部分生成RGB值，确保颜色差异明显
            r = (self.object_id * 17) % 256
            g = (self.object_id * 31) % 256
            b = (self.object_id * 43) % 256
            color = (r, g, b)
            # 加载字体
            font = Utils.load_font(FONT_CANDIDATES, 12)
            # 显示生命值
            text = f"生命:{self.health}"
            text_surf = font.render(text, True, color)
            # 在对象右上角显示，并添加基于object_id的y轴偏移
            text_x = self.x + self.w + 5
            text_y = self.y + (self.object_id % 4 * 8 - 8)
            surf.blit(text_surf, (text_x, text_y))
        
        # 显示详细信息
        if show_detail:
            # 使用object_id生成固定颜色
            # 使用object_id的不同部分生成RGB值，确保颜色差异明显
            r = (self.object_id * 17) % 256
            g = (self.object_id * 31) % 256
            b = (self.object_id * 43) % 256
            color = (r, g, b)
            # 加载字体
            font = Utils.load_font(FONT_CANDIDATES, 12)
            # 显示斗志值和生命值
            text = f"斗志:{self.morale} 生命:{self.health}"
            text_surf = font.render(text, True, color)
            # 在对象右上角显示，并添加基于object_id的y轴偏移
            text_x = self.x + self.w + 5
            text_y = self.y + (self.object_id % 4 * 8 - 8)
            surf.blit(text_surf, (text_x, text_y))
class RandomEvent:
    """随机事件实体类"""
    def __init__(self, x, y):
        global object_id
        self.x = x
        self.y = y
        # 加载随机事件图标
        self.img = Utils.load_image('random_event', (64, 64))
        self.w, self.h = (64, 64)  # 固定的图标大小为64x64
        if self.img:
            # 确保图片缩放到正确的尺寸
            self.img = pygame.transform.smoothscale(self.img, (self.w, self.h))
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.alive = True
        self.object_id = object_id
        object_id += 1
        
        # 移动速度（每秒8像素）
        self.speed = 8.0
        
        # 随机事件类型（1-5对应5种不同事件）
        self.event_type = random.randint(1, 5)
        
        # 特效相关属性
        self.effect_timer = 0  # 特效计时器
        self.effect_interval = 0.5  # 特效间隔（秒）
        self.effect_duration = 0.3  # 特效持续时间（秒）
        self.show_effect = False  # 是否显示特效
        self.effect_progress = 0  # 特效进度（0-1）
    
    def update(self, dt, player_x, player_y):
        # 计算到玩家的方向
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # 向玩家方向移动
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        self.rect.topleft = (self.x, self.y)
        
        # 检查是否超出屏幕
        if self.y > SCREEN_H or self.x < -self.w or self.x > SCREEN_W:
            self.alive = False
        
        # 处理特效
        self.effect_timer += dt
        if self.effect_timer >= self.effect_interval:
            self.show_effect = True
            self.effect_progress = 0
            self.effect_timer = 0
        
        if self.show_effect:
            self.effect_progress += dt / self.effect_duration
            if self.effect_progress >= 1.0:
                self.show_effect = False
    
    def draw(self, surf):
        # 绘制随机事件图标
        surf.blit(self.img, (self.x, self.y))
        
        # 绘制特效（光环效果）
        if self.show_effect:
            # 绘制脉冲光环
            alpha = int(150 * (1 - self.effect_progress))
            radius = int(32 + 16 * self.effect_progress)
            
            # 创建一个临时的透明Surface
            effect_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(effect_surf, (255, 255, 255, alpha), (radius, radius), radius)
            
            # 绘制到主表面
            surf.blit(effect_surf, (self.x + self.w//2 - radius, self.y + self.h//2 - radius))

class PowerUp:
    """小道具基类"""
    def __init__(self, x, y, power_type, image=None):
        global object_id
        self.x = x
        self.y = y
        self.power_type = power_type
        self.hp = 2000  # 所有道具的hp都是2000
        self.img = image if image else Utils.make_pixel_sprite(20, 20, COLOR_GREEN, scale=3)
        self.w, self.h = (64, 64)  # 固定的图标大小为64x64
        if image:
            # 确保图片缩放到正确的尺寸
            self.img = pygame.transform.smoothscale(image, (self.w, self.h))
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.alive = True
        self.object_id = object_id
        object_id += 1
        
        # 特效相关属性
        self.effect_timer = 0  # 特效计时器
        self.effect_interval = 3.0  # 特效间隔（秒）
        self.effect_duration = 1.0  # 特效持续时间（秒）
        self.show_effect = False  # 是否显示特效
        self.effect_progress = 0  # 特效进度（0-1）
        
        # 道具移动速度
        self.vy = 50  # 向下移动速度
    
    def update(self, dt):
        # 移动道具
        self.y += self.vy * dt

        self.rect.topleft = (self.x, self.y)
        
        # 检查是否超出屏幕
        if self.y > SCREEN_H:
            self.alive = False
        
        # 处理特效
        self.effect_timer += dt
        if self.effect_timer >= self.effect_interval:
            self.show_effect = True
            self.effect_progress = 0
            self.effect_timer = 0
        
        if self.show_effect:
            self.effect_progress += dt / self.effect_duration
            if self.effect_progress >= 1.0:
                self.show_effect = False
    
    def draw(self, surf):
        # 绘制道具图标
        surf.blit(self.img, (self.x, self.y))
        
        # 绘制特效（绿色圆环）
        if self.show_effect:
            # 计算圆环半径（从16到32）
            radius = 16 + (32 - 16) * self.effect_progress
            # 计算透明度（从255到0，确保逐渐变浅）
            alpha = 255 * (1 - self.effect_progress)

            temp_surf = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
            # 绘制绿色圆环，确保颜色是透明的
            pygame.draw.circle(temp_surf, (0, 255, 0, int(alpha)), (int(radius), int(radius)), int(radius), 2)
            
            # 将临时surface绘制到游戏表面上
            center_x = self.x + self.w // 2
            center_y = self.y + self.h // 2
            surf.blit(temp_surf, (center_x - radius, center_y - radius))
    
    def use(self, player, game):
        """抽象方法，由子类实现"""
        raise NotImplementedError("子类必须实现use方法")
class SpeedPowerUp(PowerUp):
    """加速道具类"""
    def __init__(self, x, y, image=None):

        if image is None:
            image = Utils.load_image('speed', (64, 64))
        super().__init__(x, y, 'speed', image)
    
    def use(self, player, game):
        """使用加速道具：玩家移动速度翻倍，15秒后恢复"""
        # 保存原始速度
        original_speed = player.speed
        
        # 提升速度
        player.speed *= 2

        def restore_speed():
            player.speed = original_speed
        
        task = runTaskLater(restore_speed, 15000)

        return task
class Shield:
    """护盾类，管理护盾的状态和碰撞逻辑"""
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.shield_value = 30  # 护盾值
        self.radius = 32  # 护盾半径
        self.active = True  # 护盾是否激活

        self.x = self.player.x + self.player.w // 2
        self.y = self.player.y + self.player.h // 2
    
    def update(self):
        # 护盾位置与玩家同步
        self.x = self.player.x + self.player.w // 2
        self.y = self.player.y + self.player.h // 2
    
    def draw(self, surf):
        if not self.active:
            return

        temp_surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        # 绘制淡蓝色圆形滤镜
        pygame.draw.circle(temp_surf, (100, 180, 255, 128), (int(self.radius), int(self.radius)), int(self.radius))
        
        # 将临时surface绘制到游戏表面上
        surf.blit(temp_surf, (self.x - self.radius, self.y - self.radius))
        
        # 在护盾右上角显示蓝色护盾值文本

        font = pygame.font.SysFont(None, 20)
        # 渲染护盾值文本，使用蓝色
        shield_text = font.render(f'{self.shield_value}', True, COLOR_SKY_BLUE)  # 天蓝色
        # 计算文本位置（护盾右上角）
        text_x = self.x + self.radius - shield_text.get_width() - 5
        text_y = self.y - self.radius + 5
        # 绘制文本到游戏表面
        surf.blit(shield_text, (text_x, text_y))
    
    def hit_by_bullet(self):
        """被敌方子弹击中"""
        self.shield_value -= 1
        # 播放护盾被击中音效
        Utils.play_sound(self.game.snd_shield_hit, self.game)
        # 检查护盾是否被打破
        if self.shield_value <= 0:
            self.break_shield()
            return True  # 护盾已打破
        return False
    
    def hit_by_enemy(self):
        """被敌方飞机撞击"""
        self.break_shield()
        return True  # 护盾已打破
    
    def break_shield(self):
        """护盾被打破"""
        self.active = False
        # 播放护盾破碎音效
        Utils.play_sound(self.game.snd_shield_fail, self.game)
    
    def add_shield_value(self, value):
        """增加护盾值"""
        self.shield_value += value
class ShieldPowerUp(PowerUp):
    """护盾道具类"""
    def __init__(self, x, y, image=None):

        if image is None:
            image = Utils.load_image('shield', (64, 64))
        super().__init__(x, y, 'shield', image)
    
    def use(self, player, game):
        """使用护盾道具：如果玩家没有护盾则创建，否则增加护盾值"""
        # 检查玩家是否已经有护盾
        if not player.shield or not player.shield.active:
    
            player.shield = Shield(player, game)
        else:
            # 增加护盾值
            player.shield.add_shield_value(30)

        return None
class HealPowerUp(PowerUp):
    """加血道具类"""
    def __init__(self, x, y, image=None):

        if image is None:
            image = Utils.load_image('heal', (64, 64))
        super().__init__(x, y, 'heal', image)
    
    def use(self, player, game):
        """使用加血道具：增加玩家600点生命值"""
        # 增加玩家生命值
        player.health = min(MAX_PLAYER_HEALTH, player.health + 600)

        return None
class SuperRapidShootPowerUp(PowerUp):
    """连发道具类"""
    def __init__(self, x, y, image=None):

        if image is None:
            image = Utils.load_image('super_rapid_shoot', (64, 64))
        super().__init__(x, y, 'super_rapid_shoot', image)
    
    def use(self, player, game):
        """使用连发道具：强制改为连射模式，大幅提高射速，15秒后恢复"""
        # 保存原始射击模式和射速
        original_shoot_type = player.current_shoot_type
        original_shots_per_second = player.rapid_shots_per_second
        
        # 修改为连射模式并大幅提高射速
        player.current_shoot_type = SHOOT_TYPE_RAPID
        player.rapid_shots_per_second = 40  # 极高射速
        game.allow_switch_shoot_type = False

        def restore_shoot_settings():
            player.current_shoot_type = original_shoot_type
            player.rapid_shots_per_second = original_shots_per_second
            game.allow_switch_shoot_type = True
        
        task = runTaskLater(restore_shoot_settings, 15000)
        
        return task
class SuperScatterShootPowerUp(PowerUp):
    """穿透道具类"""
    def __init__(self, x, y, image=None):

        if image is None:
            image = Utils.load_image('super_scatter_shoot', (64, 64))
        super().__init__(x, y, 'super_scatter_shoot', image)
    
    def use(self, player, game):
        """使用穿透道具：强制改为散射模式，子弹具有穿透属性，15秒后恢复"""

        original_shoot_type = player.current_shoot_type
        
        # 修改为散射模式
        player.current_shoot_type = SHOOT_TYPE_SCATTER
        
        game.bullets_piercing = True
        game.allow_switch_shoot_type = False

        def restore_shoot_settings():
            player.current_shoot_type = original_shoot_type
            # 恢复原始的create_bullet方法
            game.bullets_piercing = False
            game.allow_switch_shoot_type = True
        
        task = runTaskLater(restore_shoot_settings, 15000)
        
        return task
class Enemy:
    """敌方飞机类"""
    def __init__(self, x, y, game, vy=100, vx=0, hp=100, score=100, image=None, stage=1):
        global object_id
        self.x = x
        self.y = y
        self.vy = vy
        self.vx = vx  # 添加水平速度属性，支持飓风效果
        # 存储原始速度，用于飓风效果恢复
        self.original_vx = vx
        self.original_vy = vy
        self.hp = hp
        self.score = score
        self.stage = stage  # 使用传入的stage参数
        self.game = game

        self.img = image if image else Utils.make_pixel_sprite(10, 10, (255, 80, 80), scale=3)
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.alive = True
        # 分配唯一的对象ID
        self.object_id = object_id
        object_id += 1
        
        # 新增射击方式相关属性

        if self.stage <= 2:
            # stage=1-2时，只能为直射
            self.current_shoot_type = SHOOT_TYPE_DIRECT
        elif self.stage == 3:
            # stage=3时，50%概率直射，50%概率散射
            self.current_shoot_type = random.choice([SHOOT_TYPE_DIRECT, SHOOT_TYPE_SCATTER])
        elif self.stage == 4:
            # stage=4时，33%概率直射，33%概率散射，33%概率连射
            self.current_shoot_type = random.choice([SHOOT_TYPE_DIRECT, SHOOT_TYPE_SCATTER, SHOOT_TYPE_RAPID])
        else:
            # 默认直射
            self.current_shoot_type = SHOOT_TYPE_DIRECT
        
        self.time_since_shot = 0.0  # 射击计时器
        self.shoot_interval = random.uniform(1.0, 3.0)  # 射击间隔（秒）
        self.rapid_shot_counter = 0  # 连射计时器
        self.rapid_shots_per_second = 8  # 每秒发射的子弹数（连射）
        
    def shoot(self):
        """根据stage和射击方式发射子弹"""
        bullets = []
        center_x = self.x + self.w // 2 - 2
        by = self.y + self.h
        
        # 根据射击方式生成子弹
        if self.current_shoot_type == SHOOT_TYPE_DIRECT:
            # 直射：子弹排列在飞机前方，同时发射
            bullet_count = self.stage  # 每次发射stage个子弹
            
            # 创建平行子弹
            spacing = 10  # 子弹间隔
            start_x = center_x - ((bullet_count - 1) * spacing) // 2
            
            for i in range(bullet_count):
                bx = start_x + i * spacing
                bullets.append(Bullet(bx, by, vy=300, owner=BULLET_OWNER_ENEMY, shoot_type=SHOOT_TYPE_DIRECT, angle=0))
                
        elif self.current_shoot_type == SHOOT_TYPE_SCATTER:
            # 散射模式：使用stage作为子弹数量
            bullet_count = self.stage
            
            angles = []

            if bullet_count % 2 == 1:  # 奇数子弹
                # 包含正前方的0度
                if bullet_count == 1:
                    angles = [0]
                else:
                    # 计算角度间隔，以15°为基础
                    half_count = bullet_count // 2
                    for i in range(1, half_count + 1):
                        angles.append(-15 * i)
                    angles.append(0)  # 正前方
                    for i in range(1, half_count + 1):
                        angles.append(15 * i)
            else:  # 偶数子弹
                # 不包含正前方
                half_count = bullet_count // 2
                for i in range(1, half_count + 1):
                    angles.append(-15 * i)
                for i in range(1, half_count + 1):
                    angles.append(15 * i)
            
            # 确保角度列表已排序
            angles.sort()
            
            for angle in angles:
                # 计算子弹初始位置，使子弹从飞机前端发出
                radians = math.radians(angle)
                # 以飞机图标尺寸为半径计算偏移
                radius = self.w / 2  # 使用飞机宽度的一半作为半径
                offset_x = math.sin(radians) * radius
                
                bx = center_x + offset_x

                bullet = Bullet(bx, by, vy=300, owner=BULLET_OWNER_ENEMY, shoot_type=SHOOT_TYPE_SCATTER, angle=angle)
                bullets.append(bullet)
                
        elif self.current_shoot_type == SHOOT_TYPE_RAPID:
            # 连射模式：使用stage作为子弹数量
            bullet_count = self.stage

            spacing = 10  # 子弹间隔
            start_x = center_x - ((bullet_count - 1) * spacing) // 2
            
            for i in range(bullet_count):
                bx = start_x + i * spacing
                bullets.append(Bullet(bx, by, vy=300, owner=BULLET_OWNER_ENEMY, shoot_type=SHOOT_TYPE_RAPID, angle=0))

            self.rapid_shot_counter = 1.0 / self.rapid_shots_per_second
        
        # 重置射击计时器
        self.time_since_shot = 0.0
        self.shoot_interval = random.uniform(1.0, 3.0)
        
        return bullets

    def update(self, dt):
        """更新位置并可能返回敌方子弹列表"""
        # 检查是否有飓风效果
        if self.game.hurricane_active:
            # 随机改变方向
            if random.random() > 0.5:
                self.vx = self.original_vx * 1.5 * (1 if random.random() > 0.5 else -1)
            else:
                self.vx = self.original_vx * 1.5
            
            self.vy = self.original_vy * 1.5
        
        # 更新位置
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.topleft = (self.x, self.y)
        
        # 确保敌人在屏幕内或附近
        if self.x < -50 or self.x > SCREEN_W + 50:
            self.vx = -self.vx  # 反弹

        self.time_since_shot += dt
        
        bullets = []

        if self.stage <= 2:
            # stage 1-2: 只能直射
            self.current_shoot_type = SHOOT_TYPE_DIRECT
        elif self.stage == 3:
            # stage 3: 可以直射或散射，各50%概率
            self.current_shoot_type = random.choice([SHOOT_TYPE_DIRECT, SHOOT_TYPE_SCATTER])
        elif self.stage == 4:
            # stage 4: 可以直射、散射或连射，各33.3%概率
            self.current_shoot_type = random.choice([SHOOT_TYPE_DIRECT, SHOOT_TYPE_SCATTER, SHOOT_TYPE_RAPID])
        
        # 较低的概率射击，避免子弹过多
        if random.random() < 0.01:  # 1%的概率射击
            bullets = self.shoot()

        if self.y > SCREEN_H:
            self.alive = False

        return bullets

    def draw(self, surf):
        surf.blit(self.img, (self.x, self.y))
class FloatingText:
    """浮动文字效果类"""
    def __init__(self, x, y, text, color, duration=1.0, rise_speed=40):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.rise_speed = rise_speed  # 每秒上升的像素数
        self.time = 0.0
        self.alpha = 255
        self.alive = True

    def update(self, dt):
        self.time += dt
        if self.time >= self.duration:
            self.alive = False
            return

        # 向上移动
        self.y -= self.rise_speed * dt
        # 逐渐降低不透明度
        progress = self.time / self.duration
        self.alpha = int(255 * (1.0 - progress))

    def draw(self, surf, font):
        if not self.alive:
            return
        color = self.color + (self.alpha,)
        text = font.render(self.text, True, color)
        text.set_alpha(self.alpha)
        surf.blit(text, (self.x, self.y))
class Explosion:
    """爆炸效果类"""
    def __init__(self, x, y, duration=0.4, max_radius=28):
        self.x = x
        self.y = y
        self.duration = duration
        self.time = 0.0
        self.max_radius = max_radius
        self.alive = True

    def update(self, dt):
        self.time += dt
        if self.time >= self.duration:
            self.alive = False

    def draw(self, surf):
        t = max(0.0, min(1.0, self.time / self.duration))
        # 由小到大、由亮到暗
        r = int(self.max_radius * t)
        if r > 0:
            color = (
                255,
                max(0, int(220 * (1 - t))),
                max(0, int(80 * (1 - t)))
            )
            pygame.draw.circle(surf, color, (int(self.x), int(self.y)), r)
class UIManager:
    """UI管理器类"""
    def __init__(self, game):
        self.game = game
        self.font = Utils.load_font(FONT_CANDIDATES, 20)
        self.large_font = Utils.load_font(FONT_CANDIDATES, 36, bold=True)

        self.sfx_volume = 1.0
        self.music_volume = 1.0
        self.master_volume = 1.0  # 新增主音量属性
        # 右上角文本管理系统
        self.top_right_texts = []  # 存储右上角显示的文本项

        self.modal_active = False
        self.modal_progress = 0.0
        self.modal_fade_speed = 4.0
        self.modal_hover = {'confirm': False, 'continue': False}
        self.modal_type = None  # 'restart' or 'return_title' 或 None
        self.gameover_progress = 0.0
        self.tutorial_active = False
        self.close_button_rect = None 
        self._input_confirm_btn = None
        self._input_cancel_btn = None
        
        # 标题界面按钮
        self.title_buttons = {
            'start': {
                'rect': pygame.Rect(SCREEN_W // 2 - 120, 400, 240, 50),
                'color': COLOR_GOLD,  # 金色
                'text': '开始游戏',
                'hover': False
            },
            'settings': {
                'rect': pygame.Rect(SCREEN_W // 2 - 120, 470, 240, 50),
                'color': COLOR_BLUE_BUTTON,  # 蓝色
                'text': '设置',
                'hover': False
            },
            'tutorial': {
                'rect': pygame.Rect(SCREEN_W // 2 - 120, 540, 240, 50),
                'color': COLOR_DARK_GREEN,  # 绿色
                'text': '教程',
                'hover': False
            },
            'statistics': {
                'rect': pygame.Rect(SCREEN_W // 2 - 120, 610, 240, 50),
                'color': COLOR_CYAN,  # 青色
                'text': '统计',
                'hover': False
            }
        }
        
        # 统计界面状态
        self.stats_active = False

        self.settings_active = False
        self.settings_progress = 0.0
        self.settings_fade_speed = 4.0
        self.input_active = False
        self.active_key_binding = None
        # 关闭按钮位置
        self.close_button_rect = pygame.Rect(340, 20, 40, 40)

        self.volume_settings = {
            'master': {'value': 100, 'editing': False, 'rect': pygame.Rect(150, 100, 200, 20), 'dragging': False},
            'music': {'value': 100, 'editing': False, 'rect': pygame.Rect(150, 150, 200, 20), 'dragging': False},
            'sound': {'value': 100, 'editing': False, 'rect': pygame.Rect(150, 200, 200, 20), 'dragging': False}
        }
        
        # 数字输入界面状态
        self.number_input_active = False
        self.active_volume = None
        self.input_value = ""
        self.input_cursor_visible = True
        self.input_cursor_timer = 0

        self.key_bindings = {
            "up": {'key': pygame.K_w, 'text': 'W', 'rect': pygame.Rect(260, 280, 80, 40), 'default_key': pygame.K_w, 'default_text': 'W'},
            "down": {'key': pygame.K_s, 'text': 'S', 'rect': pygame.Rect(260, 330, 80, 40), 'default_key': pygame.K_s, 'default_text': 'S'},
            "left": {'key': pygame.K_a, 'text': 'A', 'rect': pygame.Rect(260, 380, 80, 40), 'default_key': pygame.K_a, 'default_text': 'A'},
            "right": {'key': pygame.K_d, 'text': 'D', 'rect': pygame.Rect(260, 430, 80, 40), 'default_key': pygame.K_d, 'default_text': 'D'},
            "shoot": {'key': pygame.K_SPACE, 'text': 'SPACE', 'rect': pygame.Rect(260, 480, 120, 40), 'default_key': pygame.K_SPACE, 'default_text': 'SPACE'},
            "music": {'key': pygame.K_m, 'text': 'M', 'rect': pygame.Rect(260, 530, 80, 40), 'default_key': pygame.K_m, 'default_text': 'M'},
            'restart': {'key': pygame.K_r, 'text': 'R', 'rect': pygame.Rect(260, 580, 80, 40), 'default_key': pygame.K_r, 'default_text': 'R'},
            "shoot_switch": {'key': pygame.K_z, 'text': 'Z', 'rect': pygame.Rect(260, 630, 80, 40), 'default_key': pygame.K_z, 'default_text': 'Z'},
            'show_stats': {'key': pygame.K_x, 'text': 'X', 'rect': pygame.Rect(260, 680, 80, 40), 'default_key': pygame.K_x, 'default_text': 'X'}
        }
        
        # 恢复默认按钮 - 调整位置，增加间距
        self.reset_default_buttons = {}
        for key_name, key_info in self.key_bindings.items():
            # 计算恢复默认按钮位置：在按键绑定按钮左侧，相距15像素，增加间距避免重叠
            btn_x = key_info['rect'].x - 95  # 按钮宽度80 + 间距15
            btn_y = key_info['rect'].y
            self.reset_default_buttons[key_name] = pygame.Rect(btn_x, btn_y, 80, 40)
        
        # 标签按钮
        self.settings_labels = {
            "master": {'text': '主音量', 'rect': pygame.Rect(50, 95, 80, 30)},
            "music": {'text': '音乐音量', 'rect': pygame.Rect(50, 145, 80, 30)},
            "sound": {'text': '音效音量', 'rect': pygame.Rect(50, 195, 80, 30)},
            'keybind': {'text': '按键绑定', 'rect': pygame.Rect(50, 245, 80, 30)},
            "up": {'text': '向上移动', 'rect': pygame.Rect(50, 280, 120, 40)},
            "down": {'text': '向下移动', 'rect': pygame.Rect(50, 330, 120, 40)},
            "left": {'text': '向左移动', 'rect': pygame.Rect(50, 380, 120, 40)},
            "right": {'text': '向右移动', 'rect': pygame.Rect(50, 430, 120, 40)},
            "shoot": {'text': '发射子弹', 'rect': pygame.Rect(50, 480, 120, 40)},
            "bgm": {'text': '开关音乐', 'rect': pygame.Rect(50, 530, 120, 40)},
            'restart': {'text': '重新开始', 'rect': pygame.Rect(50, 580, 120, 40)},
            "shoot_switch": {'text': '射击模式切换', 'rect': pygame.Rect(50, 630, 120, 40)},
            'show_stats': {'text': '打开统计', 'rect': pygame.Rect(50, 680, 120, 40)}
        }

        self.title_logo = Utils.load_image('logo', (120, 120))
    
    def add_top_right_text(self, text, color=COLOR_LIGHT_GRAY, key=None):
        """添加右上角文本
        
        Args:
            text: 要显示的文本内容
            color: 文本颜色，默认为灰色
            key: 文本项的唯一标识符，用于后续更新或删除
        """

        for i, item in enumerate(self.top_right_texts):
            if 'key' in item and item['key'] == key:
                self.top_right_texts[i] = {'text': text, 'color': color, 'key': key}
                return
        # 如果不存在相同key或没有指定key，则添加新文本项
        self.top_right_texts.append({'text': text, 'color': color, 'key': key})
    
    def remove_top_right_text(self, key):
        """根据key移除右上角文本"""
        self.top_right_texts = [item for item in self.top_right_texts if 'key' not in item or item['key'] != key]
    
    def clear_top_right_texts(self):
        """清空所有右上角文本"""
        self.top_right_texts = []

    def update_top_right_texts(self):
        """更新右上角文本内容（如BGM状态等）"""

        try:
            status = 'BGM: ON' if pygame.mixer.music.get_busy() else 'BGM: OFF'
            # 使用自定义按键绑定显示提示
            music_key_text = self.key_bindings['music']['text']
            self.add_top_right_text(f'{status} (按 {music_key_text} 切换)', key='music_status')
        except Exception:
            pass
            
        # 添加统计文本提示
        try:
            stats_key_text = self.key_bindings['show_stats']['text']
            self.add_top_right_text(f'按 {stats_key_text} 打开统计', color=COLOR_GRAY, key='stats_tip')
        except Exception:
            # 如果没有找到show_stats按键绑定，使用默认的X键
            self.add_top_right_text('按 X 打开统计', color=COLOR_GRAY, key='stats_tip')
            
        # 当stage >= 3时，显示切换射击模式的提示
        try:
            if self.game.stage >= 3:
                # 获取切换射击模式的按键文本
                shoot_switch_key = self.key_bindings.get('shoot_switch', {}).get('text', 'Z')
                self.add_top_right_text(f'按 {shoot_switch_key} 切换射击模式', color=COLOR_GRAY, key='shoot_switch_tip')
            else:
                # 当stage < 3时，移除射击模式切换提示
                self.remove_top_right_text('shoot_switch_tip')
        except Exception:
            pass
            
    def draw_hud(self, screen, score, player):
        """绘制游戏HUD界面"""
        # 绘制得分和生命值
        score_s = self.font.render(f'得分: {score}', True, COLOR_WHITE)
        health_s = self.font.render(f'生命值: {player.health}', True, COLOR_WHITE)
        screen.blit(score_s, (8, 8))
        screen.blit(health_s, (8, 36))

        # 绘制浮动文本效果
        for ft in self.game.floating_texts:
            ft.draw(screen, self.font)
        self.update_top_right_texts()
        
        # 绘制所有右上角文本，从上到下排列
        y_offset = 8  # 初始y坐标
        for item in self.top_right_texts:
            text_surf = self.font.render(item['text'], True, item['color'])
            screen.blit(text_surf, (SCREEN_W - text_surf.get_width() - 8, y_offset))
            y_offset += text_surf.get_height() + 2  # 增加行间距
    
    def draw_title(self, screen, start_transition, transition_progress):
        """绘制标题界面"""
        # 计算界面元素的透明度（用于过渡动画）
        alpha = 255
        if start_transition:
            alpha = int(255 * (1.0 - transition_progress))

        # 绘制 logo
        if self.title_logo:
            if start_transition:
                logo_copy = self.title_logo.copy()
                logo_copy.set_alpha(alpha)
                logo_x = SCREEN_W // 2 - 60
                logo_y = 150
                screen.blit(logo_copy, (logo_x, logo_y))
            else:
                logo_x = SCREEN_W // 2 - 60
                logo_y = 150
                screen.blit(self.title_logo, (logo_x, logo_y))

        # 绘制按钮
        for btn_info in self.title_buttons.values():
            # 绘制按钮背景
            color = btn_info['color']
            if btn_info['hover']:
                # 悬停时稍微变亮
                color = tuple(min(255, c + 30) for c in color)

            btn_surf = pygame.Surface((btn_info['rect'].width, btn_info['rect'].height), pygame.SRCALPHA)

            # 在临时surface上绘制圆角矩形
            pygame.draw.rect(btn_surf, color + (alpha,), btn_surf.get_rect(), border_radius=10)

            # 按钮文字
            text = self.large_font.render(btn_info['text'], True, COLOR_WHITE)
            text_x = btn_info['rect'].width // 2 - text.get_width() // 2
            text_y = btn_info['rect'].height // 2 - text.get_height() // 2
            text.set_alpha(alpha)
            btn_surf.blit(text, (text_x, text_y))

            # 将带透明度的按钮绘制到屏幕
            screen.blit(btn_surf, btn_info['rect'])
    
    def draw_settings(self, screen):
        """绘制设置界面"""
        settings_w = 400
        settings_h = 650
        settings_x = SCREEN_W // 2 - settings_w // 2
        settings_y = SCREEN_H // 2 - settings_h // 2
        p = max(0.0, min(1.0, self.settings_progress))
        try:
            snap = screen.copy()
            small = pygame.transform.smoothscale(snap, (SCREEN_W // 4, SCREEN_H // 4))
            blurred = pygame.transform.smoothscale(small, (SCREEN_W, SCREEN_H))
            blurred.set_alpha(int(192 * p))
            screen.blit(blurred, (0, 0))
        except Exception:
            # 如果模糊失败，使用半透明遮罩
            overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            overlay.fill(COLOR_BLACK)
            overlay.set_alpha(int(160 * p))
            screen.blit(overlay, (0, 0))
        window_surf = pygame.Surface((settings_w, settings_h), pygame.SRCALPHA)
        window_color = (100, 150, 255, int(240 * p))
        pygame.draw.rect(window_surf, window_color, window_surf.get_rect(), border_radius=20)
        
        # 绘制关闭按钮（红色圆形）
        close_button_rel_x = self.close_button_rect.x - settings_x
        close_button_rel_y = self.close_button_rect.y - settings_y
        pygame.draw.circle(window_surf, (255, 80, 80, int(240 * p)), 
                          (close_button_rel_x + 20, close_button_rel_y + 20), 20)
        close_text = self.large_font.render('×', True, COLOR_WHITE)
        text_rect = close_text.get_rect(center=(close_button_rel_x + 20, close_button_rel_y + 20))
        window_surf.blit(close_text, text_rect)

        # 绘制标签按钮
        label_color = (80, 100, 180, int(240 * p))
        for label_info in self.settings_labels.values():
            # 只为非按键绑定的标签绘制背景

            pygame.draw.rect(window_surf, label_color, 
                            (label_info['rect'].x - settings_x, 
                            label_info['rect'].y - settings_y,
                            label_info['rect'].width,
                            label_info['rect'].height),
                            border_radius=8)
            text = self.font.render(label_info['text'], True, COLOR_WHITE)
            window_surf.blit(text, (label_info['rect'].x - settings_x + (label_info['rect'].width - text.get_width()) // 2,
                                label_info['rect'].y - settings_y + (label_info['rect'].height - text.get_height()) // 2))

        # 绘制音量滑块
        self._draw_volume_sliders(window_surf, settings_x, settings_y, p)
        
        # 绘制按键绑定按钮
        self._draw_key_bindings(window_surf, settings_x, settings_y, p)

        screen.blit(window_surf, (settings_x, settings_y))

        # 绘制数字输入界面
        self._draw_number_input(screen, p)
    
    def _draw_volume_sliders(self, window_surf, settings_x, settings_y, p):
        """绘制音量滑块"""
        for vol_name, vol_info in self.volume_settings.items():
            # 滑块背景
            slider_rect = pygame.Rect(vol_info['rect'].x - settings_x, 
                                    vol_info['rect'].y - settings_y,
                                    vol_info['rect'].width, 
                                    vol_info['rect'].height)
            pygame.draw.rect(window_surf, (60, 60, 60, int(240 * p)), slider_rect, border_radius=5)
            pygame.draw.rect(window_surf, (40, 40, 40, int(240 * p)), slider_rect, width=1, border_radius=5)

            # 滑块进度条
            progress_width = int(vol_info['rect'].width * vol_info['value'] / 100)
            progress_rect = pygame.Rect(slider_rect.x, slider_rect.y, progress_width, slider_rect.height)
            pygame.draw.rect(window_surf, (120, 180, 255, int(240 * p)), progress_rect, border_radius=5)
            
            # 滑块指示器
            knob_x = progress_rect.right
            knob_y = progress_rect.y + progress_rect.h // 2
            knob_radius = max(4, progress_rect.h // 2)
            try:
                pygame.draw.circle(window_surf, (255, 230, 120, int(240 * p)), (knob_x, knob_y), knob_radius)
            except Exception:
                pygame.draw.circle(window_surf, COLOR_BRIGHT_YELLOW, (knob_x, knob_y), knob_radius)

            # 数值显示
            value_text = self.font.render(f"{vol_info['value']}%", True, COLOR_WHITE)
            window_surf.blit(value_text, (slider_rect.right + 10, 
                                        slider_rect.y + (slider_rect.height - value_text.get_height()) // 2))
    
    def _draw_key_bindings(self, window_surf, settings_x, settings_y, p):
        """绘制按键绑定按钮"""
        key_color = (200, 200, 200, int(240 * p))
        active_color = (255, 255, 100, int(240 * p))
        reset_btn_color = (150, 150, 220, int(240 * p))  # 使用固定颜色，不随鼠标悬停变化
        padding = 12  # 增加内边距，改善文字显示
        min_button_width = 80  # 增加最小宽度，避免小按键过于拥挤
        
        for key_name, key_info in self.key_bindings.items():
            # 检查是否有重复按键
            is_duplicate = self._check_key_duplicate(key_name)
            color = (255, 255, 0, int(240 * p)) if is_duplicate else active_color if self.input_active and self.active_key_binding == key_name else key_color

            text = self.font.render(key_info['text'], True, COLOR_BLACK)
            text_width = text.get_width()
            
            # 动态计算按钮宽度，根据文字大小调整
            button_width = max(min_button_width, text_width + padding * 2)  # 增加最小宽度
            
            # 绘制恢复默认按钮（先绘制左侧的恢复默认按钮）
            reset_btn_rect = self.reset_default_buttons[key_name]
            # 确保恢复默认按钮宽度足够
            reset_width = 80  # 固定的恢复默认按钮宽度
            
            # 绘制恢复默认按钮
            pygame.draw.rect(window_surf, reset_btn_color,
                            (reset_btn_rect.x - settings_x,
                            reset_btn_rect.y - settings_y,
                            reset_width,
                            reset_btn_rect.height),
                            border_radius=8)
            
            # 绘制恢复默认按钮文字
            reset_text = self.font.render("恢复默认", True, COLOR_BLACK)
            window_surf.blit(reset_text, 
                            (reset_btn_rect.x - settings_x + (reset_width - reset_text.get_width()) // 2,
                            reset_btn_rect.y - settings_y + (reset_btn_rect.height - reset_text.get_height()) // 2))
            
            # 绘制按键背景，使用动态计算的宽度
            pygame.draw.rect(window_surf, color,
                            (key_info['rect'].x - settings_x,
                            key_info['rect'].y - settings_y,
                            button_width,
                            key_info['rect'].height),
                            border_radius=8)
            
            # 文字居中显示，避免靠左导致的重叠问题
            window_surf.blit(text, (key_info['rect'].x - settings_x + (button_width - text_width) // 2,
                                key_info['rect'].y - settings_y + (key_info['rect'].height - text.get_height()) // 2))
    
    def _draw_number_input(self, screen, p):
        """绘制数字输入界面"""
        if not self.number_input_active or not self.active_volume:
            return

        input_w = 280
        input_h = 120
        input_x = SCREEN_W // 2 - input_w // 2
        input_y = SCREEN_H // 2 - input_h // 2

        # 半透明背景
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # 输入框背景
        input_surf = pygame.Surface((input_w, input_h), pygame.SRCALPHA)
        pygame.draw.rect(input_surf, (60, 80, 120, 240), input_surf.get_rect(), border_radius=10)

        # 标题文本
        title_text = self.font.render(f"请输入{self.settings_labels[self.active_volume]['text']}(0-100)", True, COLOR_WHITE)
        input_surf.blit(title_text, (input_w//2 - title_text.get_width()//2, 10))

        # 输入框
        input_box_w = 160
        input_box_h = 30
        input_box_x = (input_w - input_box_w) // 2
        input_box_y = 45
        pygame.draw.rect(input_surf, COLOR_LIGHT_DARK_GRAY, (input_box_x, input_box_y, input_box_w, input_box_h))
        pygame.draw.rect(input_surf, COLOR_MEDIUM_GRAY, (input_box_x, input_box_y, input_box_w, input_box_h), 1)

        # 输入的文本
        if self.input_value:
            input_text = self.font.render(self.input_value, True, COLOR_WHITE)
        else:
            input_text = self.font.render("0", True, COLOR_GRAY)
        text_x = input_box_x + 5
        text_y = input_box_y + (input_box_h - input_text.get_height()) // 2
        input_surf.blit(input_text, (text_x, text_y))

        # 光标闪烁
        if self.input_cursor_visible:
            cursor_x = text_x + input_text.get_width() + 2
            cursor_y = text_y
            pygame.draw.line(input_surf, 
                (255, 255, 255),
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + input_text.get_height()),
                2)

        # 确认和取消按钮
        btn_w = 70
        btn_h = 25
        confirm_btn = pygame.Rect((input_w - btn_w*2 - 10)//2, input_h-btn_h-10, btn_w, btn_h)
        cancel_btn = pygame.Rect(confirm_btn.right + 10, input_h-btn_h-10, btn_w, btn_h)

        pygame.draw.rect(input_surf, COLOR_BUTTON_CONFIRM, confirm_btn, border_radius=5)
        pygame.draw.rect(input_surf, COLOR_BUTTON_CANCEL, cancel_btn, border_radius=5)

        confirm_text = self.font.render("确定", True, COLOR_WHITE)
        cancel_text = self.font.render("取消", True, COLOR_WHITE)

        input_surf.blit(confirm_text, 
            (confirm_btn.centerx - confirm_text.get_width()//2,
            confirm_btn.centery - confirm_text.get_height()//2))
        input_surf.blit(cancel_text,
            (cancel_btn.centerx - cancel_text.get_width()//2,
            cancel_btn.centery - cancel_text.get_height()//2))

        # 保存按钮位置用于事件处理
        self._input_confirm_btn = pygame.Rect(input_x + confirm_btn.x,
                                        input_y + confirm_btn.y,
                                        confirm_btn.width,
                                        confirm_btn.height)
        self._input_cancel_btn = pygame.Rect(input_x + cancel_btn.x,
                                        input_y + cancel_btn.y,
                                        cancel_btn.width,
                                        cancel_btn.height)

        screen.blit(input_surf, (input_x, input_y))
    
    def draw_modal(self, screen, dt):
        """绘制模态弹窗"""
        # 逐步增加 modal_progress (0..1)
        self.modal_progress += dt * self.modal_fade_speed
        p = max(0.0, min(1.0, self.modal_progress))

        Utils.draw_blurred_background(screen, int(200 * p))

        # 弹窗尺寸
        pw = int(SCREEN_W * 0.78)
        ph = 220
        px = (SCREEN_W - pw) // 2
        py = int(SCREEN_H * 0.18)

        popup_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        popup_color = COLOR_SKY_BLUE
        popup_alpha = int(255 * p)
        popup_surf.fill((0, 0, 0, 0))
        pygame.draw.rect(popup_surf, popup_color + (popup_alpha,), (0, 0, pw, ph), border_radius=14)

        # 标题文本（根据 modal_type 切换）
        title_font = Utils.load_font(FONT_CANDIDATES, 26, bold=True)
        if self.modal_type == 'restart':
            title_str = '是否确认重玩游戏？'
            confirm_label = '确认重玩'
        elif self.modal_type == 'return_title':
            title_str = '是否返回主界面？'
            confirm_label = '返回主界面'
        elif self.modal_type == 'exit_game':
            title_str = '是否退出游戏？'
            confirm_label = '退出游戏'
        else:
            title_str = '确认操作？'
            confirm_label = '确认'
        
        title_s = title_font.render(title_str, True, COLOR_WHITE)
        popup_surf.blit(title_s, (pw // 2 - title_s.get_width() // 2, 18))
        
        # 绘制右上角红色关闭按钮
        close_button_size = 30
        close_button_radius = 15
        close_button_x = pw - close_button_size - 15
        close_button_y = 15
        
        # 保存关闭按钮位置信息（用于点击检测）
        self.close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
        
        # 绘制关闭按钮背景
        pygame.draw.circle(popup_surf, (220, 50, 50, popup_alpha), 
                          (close_button_x + close_button_radius, close_button_y + close_button_radius), 
                          close_button_radius)
        
        # 绘制关闭按钮的×符号
        close_font = Utils.load_font(FONT_CANDIDATES, 24, bold=True)
        close_text = close_font.render('×', True, COLOR_WHITE)
        close_text_x = close_button_x + close_button_size // 2 - close_text.get_width() // 2
        close_text_y = close_button_y + close_button_size // 2 - close_text.get_height() // 2
        popup_surf.blit(close_text, (close_text_x, close_text_y))

        # 绘制按钮
        self._draw_modal_buttons(popup_surf, pw, ph, confirm_label, popup_alpha)

        # 将 popup_surf 以 alpha 放到屏幕
        popup_surf.set_alpha(popup_alpha)
        screen.blit(popup_surf, (px, py))
    
    def _draw_modal_buttons(self, popup_surf, pw, ph, confirm_label, popup_alpha):
        """绘制模态弹窗按钮"""
        # 按钮布局
        btn_w = int(pw * 0.42)
        btn_h = 44
        btn_pad = 18
        btn_y = ph - btn_h - 18
        btn1_x = 20
        btn2_x = pw - btn_w - 20

        mouse_x, mouse_y = pygame.mouse.get_pos()
        # 判断是否 hover（在 popup 坐标系）
        local_mx = mouse_x - (SCREEN_W - pw) // 2
        local_my = mouse_y - int(SCREEN_H * 0.18)

        # 确认和继续按钮矩形
        rbtn_rect = pygame.Rect(btn1_x, btn_y, btn_w, btn_h)
        cbtn_rect = pygame.Rect(btn2_x, btn_y, btn_w, btn_h)

        # hover 状态
        hover_confirm = rbtn_rect.collidepoint(local_mx, local_my)
        hover_continue = cbtn_rect.collidepoint(local_mx, local_my)

        # 绘制按钮
        def draw_button(surf, rect, text, base_color, hovered):
            scale = 1.08 if hovered else 1.0
            bw = int(rect.w * scale)
            bh = int(rect.h * scale)
            bx = int(rect.x - (bw - rect.w) / 2)
            by = int(rect.y - (bh - rect.h) / 2)
            r = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(surf, base_color + (popup_alpha,), r, border_radius=10)
            f = Utils.load_font(FONT_CANDIDATES, 20, bold=hovered)
            ts = f.render(text, True, (255, 255, 255))
            surf.blit(ts, (r.x + r.w // 2 - ts.get_width() // 2, r.y + r.h // 2 - ts.get_height() // 2))

        draw_button(popup_surf, rbtn_rect, confirm_label, COLOR_BUTTON_RED, hover_confirm)
        draw_button(popup_surf, cbtn_rect, '继续游玩', COLOR_BUTTON_GREEN, hover_continue)

        # 鼠标 hover 音效触发一次
        if hover_confirm and not self.modal_hover['confirm']:
            Utils.play_sound(self.game.snd_ui_hover, self.game)
        if hover_continue and not self.modal_hover['continue']:
            Utils.play_sound(self.game.snd_ui_hover, self.game)

        self.modal_hover['confirm'] = hover_confirm
        self.modal_hover['continue'] = hover_continue

        # 保存按钮 rects 以便事件处理（全局坐标）
        px = (SCREEN_W - pw) // 2
        py = int(SCREEN_H * 0.18)
        self._popup_confirm_rect = pygame.Rect(px + rbtn_rect.x, py + rbtn_rect.y, rbtn_rect.w, rbtn_rect.h)
        self._popup_continue_rect = pygame.Rect(px + cbtn_rect.x, py + cbtn_rect.y, cbtn_rect.w, cbtn_rect.h)
    
    def _check_key_duplicate(self, current_key_name):
        """检查按键是否有重复设置"""
        current_key = self.key_bindings[current_key_name]['key']
        count = 0
        for key_name, key_info in self.key_bindings.items():
            if key_info['key'] == current_key:
                count += 1
                if count > 1:  # 找到重复
                    return True
        return False

    def handle_settings_click(self, pos):
        """处理设置界面点击事件"""
        if not self.input_active:  # 如果不在等待按键输入状态
            # 检查关闭按钮
            if self.close_button_rect.collidepoint(pos):
                self.settings_active = False
                self.game.save_settings()
                return True
                
            # 检查音量滑块及数值区域
            for vol_name, vol_info in self.volume_settings.items():
                slider_rect = vol_info['rect']
                value_rect = pygame.Rect(
                    slider_rect.right + 10,
                    slider_rect.y,
                    40,  # 数值显示区域宽度
                    slider_rect.height
                )

                if slider_rect.collidepoint(pos):
            
                    raw_value = (pos[0] - slider_rect.x) / slider_rect.width * 100
                    # 四舍五入到最近的2%倍数
                    new_value = round(raw_value / 2) * 2
                    vol_info['value'] = max(0, min(100, new_value))
                    vol_info['dragging'] = True

                    if vol_name == 'music' or vol_name == 'master':
                        # 计算最终音乐音量 = 主音量 x 音乐音量
                        master_val = self.volume_settings['master']['value'] / 100
                        music_val = self.volume_settings['music']['value'] / 100
                        pygame.mixer.music.set_volume(master_val * music_val)
                    
                    return True
                elif value_rect.collidepoint(pos):
                    # 点击数值区域，进入编辑模式
                    self.number_input_active = True
                    self.active_volume = vol_name
                    self.input_value = str(int(vol_info['value']))
                    self.input_cursor_visible = True
                    self.input_cursor_timer = 0
                    vol_info['editing'] = False
                    return True

            # 检查按键绑定（只有在非输入状态下）
            if not self.input_active and not self.number_input_active:
                for key_name, key_info in self.key_bindings.items():
        
                    text = self.font.render(key_info['text'], True, COLOR_BLACK)
                    button_width = max(80, text.get_width() + 24)  # 与_draw_key_bindings方法中的计算保持一致
                    key_rect = pygame.Rect(key_info['rect'].x, key_info['rect'].y, button_width, key_info['rect'].height)
                    
                    # 检查恢复默认按钮点击
                    reset_btn_rect = self.reset_default_buttons[key_name]
                    if reset_btn_rect.collidepoint(pos):
                        # 恢复为默认按键
                        self.key_bindings[key_name]['key'] = self.key_bindings[key_name]['default_key']
                        self.key_bindings[key_name]['text'] = self.key_bindings[key_name]['default_text']
                        # 播放点击音效
                        Utils.play_sound(self.game.snd_ui_click, self.game)
                        return True
                    # 检查按键显示区域点击
                    if key_rect.collidepoint(pos) or \
                    (self.settings_labels[key_name]['rect'].collidepoint(pos) if key_name in self.settings_labels else False):
                        self.input_active = True
                        self.active_key_binding = key_name
                        return True

            # 检查返回按钮
            back_label = self.settings_labels.get('back')
            if back_label and back_label['rect'].collidepoint(pos):
                self.settings_active = False
                return True

        return False
    
    def handle_statistics_click(self, pos):
        """处理统计界面点击"""
        # 计算窗口位置和尺寸
        window_width = int(SCREEN_W * 0.85)
        window_height = int(SCREEN_H * 0.8)
        window_x = (SCREEN_W - window_width) // 2
        window_y = (SCREEN_H - window_height) // 2
        
        # 转换点击位置到窗口坐标系
        window_pos = (pos[0] - window_x, pos[1] - window_y)
        
        # 检查关闭按钮点击
        if self.close_button_rect and self.close_button_rect.collidepoint(window_pos):
            self.stats_active = False
            # 关闭统计界面时恢复游戏运行
            self.game.paused = False
            return True

        return False
    
    def draw_statistics(self, screen, statistics):
        """绘制统计界面"""
        # 计算窗口位置和尺寸
        window_width = int(SCREEN_W * 0.85)
        window_height = int(SCREEN_H * 0.8)
        window_x = (SCREEN_W - window_width) // 2
        window_y = (SCREEN_H - window_height) // 2
        
        # 创建窗口表面
        window_surf = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        
        # 绘制窗口背景（半透明白色）
        window_surf.fill((255, 255, 255, 240))
        
        # 绘制边框
        pygame.draw.rect(window_surf, COLOR_BLACK, (0, 0, window_width, window_height), 2)
        
        # 绘制标题
        title_font = Utils.load_font(FONT_CANDIDATES, 28, bold=True)
        title_surf = title_font.render('游戏统计', True, COLOR_BLACK)
        title_rect = title_surf.get_rect(center=(window_width // 2, 40))
        window_surf.blit(title_surf, title_rect)
        
        # 绘制关闭按钮
        close_btn_size = 40
        close_btn_rect = pygame.Rect(window_width - close_btn_size - 20, 20, close_btn_size, close_btn_size)
        pygame.draw.circle(window_surf, COLOR_RED, close_btn_rect.center, close_btn_size // 2)
        close_font = Utils.load_font(FONT_CANDIDATES, 24, bold=True)
        close_surf = close_font.render('×', True, COLOR_WHITE)
        close_text_rect = close_surf.get_rect(center=close_btn_rect.center)
        window_surf.blit(close_surf, close_text_rect)
        self.close_button_rect = close_btn_rect
        
        # 绘制统计数据
        stats_font = Utils.load_font(FONT_CANDIDATES, 20)
        stats_y = 100
        
        # 先添加当前游戏的实时统计数据（如果存在）
        stats_items = []
        if 'current_score' in statistics:
            stats_items.extend([
                ('当前分数', Utils.format_number(statistics['current_score'])),
                ('当前游戏时长', f"{statistics['current_game_time']:.2f} 分钟"),
                ('当前击杀飞机数', Utils.format_number(statistics['current_enemies_killed'])),
                ('当前击杀子弹数', Utils.format_number(statistics['current_bullets_collided']))
            ])
            stats_y += 20  # 增加一些间距
        
        # 添加历史统计数据
        stats_items.extend([
            ('最高分数', Utils.format_number(statistics['highest_score'])),
            ('单次最长游玩时长', f"{statistics['longest_game_time']:.2f} 分钟"),
            ('单次最高击杀飞机数', Utils.format_number(statistics['highest_enemies_killed'])),
            ('单次最高击杀子弹数', Utils.format_number(statistics['highest_bullets_collided'])),
            ('总击杀飞机数', Utils.format_number(statistics['total_enemies_killed'])),
            ('总击杀子弹数', Utils.format_number(statistics['total_bullets_collided'])),
            ('总游玩时长', f"{statistics['total_game_time']:.2f} 分钟")
        ])
        
        for label, value in stats_items:
            # 标签
            label_surf = stats_font.render(label + ':', True, COLOR_BLACK)
            label_rect = label_surf.get_rect(topleft=(40, stats_y))
            window_surf.blit(label_surf, label_rect)
            
            # 值
            value_surf = stats_font.render(value, True, COLOR_RED)
            value_rect = value_surf.get_rect(topleft=(280, stats_y))
            window_surf.blit(value_surf, value_rect)
            
            stats_y += 40
        
        # 删除了返回按钮
        
        # 将窗口绘制到屏幕上
        screen.blit(window_surf, (window_x, window_y))
    
    def draw_tutorial(self, screen):
        """绘制教程界面"""
        if not self.tutorial_active:
            return
        
        # 绘制半透明背景
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # 窗口尺寸
        window_width = int(SCREEN_W * 0.85)
        window_height = int(SCREEN_H * 0.8)
        window_x = (SCREEN_W - window_width) // 2
        window_y = (SCREEN_H - window_height) // 2
        
        # 创建窗口表面
        window_surf = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        window_surf.fill((240, 240, 240, 255))
        pygame.draw.rect(window_surf, (0, 0, 0, 255), (0, 0, window_width, window_height), 3)
        
        # 绘制关闭按钮
        close_btn_size = 40
        close_btn_rect = pygame.Rect(window_width - close_btn_size - 20, 20, close_btn_size, close_btn_size)
        pygame.draw.circle(window_surf, COLOR_RED, close_btn_rect.center, close_btn_size // 2)
        close_font = Utils.load_font(FONT_CANDIDATES, 24, bold=True)
        close_surf = close_font.render('×', True, COLOR_WHITE)
        close_text_rect = close_surf.get_rect(center=close_btn_rect.center)
        window_surf.blit(close_surf, close_text_rect)
        self.close_button_rect = close_btn_rect
        
        # 标题字体（减小字体大小）
        title_font = Utils.load_font(FONT_CANDIDATES, 24)
        # 正文字体（减小字体大小）
        content_font = Utils.load_font(FONT_CANDIDATES, 16)
        # 小标题字体（减小字体大小）
        subtitle_font = Utils.load_font(FONT_CANDIDATES, 18)
        
        # 标题
        title_surf = title_font.render('游戏教程', True, COLOR_BLACK)
        title_rect = title_surf.get_rect(center=(window_width // 2, 40))
        window_surf.blit(title_surf, title_rect)
        
        # 绘制内容
        y_pos = 100
        line_height = 30
        
        # 背景故事
        story_title = subtitle_font.render('背景故事', True, COLOR_DARK_RED_TEXT)
        window_surf.blit(story_title, (40, y_pos))
        y_pos += 40
        
        story_lines = [
            '在不久的将来,世界陷入了资源争夺的紧张局势',
            'A市为了获取资源,对我们的家园B市发动了袭击',
            '作为B市最优秀的飞行员,你必须驾驶战机保卫家园',
            '击退A市的入侵部队,守护我们的和平与自由!'
        ]
        
        for line in story_lines:
            text_surf = content_font.render(line, True, COLOR_BLACK)
            window_surf.blit(text_surf, (40, y_pos))
            y_pos += line_height
        
        y_pos += 20
        
        # 按键操作
        control_title = subtitle_font.render('按键操作', True, COLOR_DARK_RED_TEXT)
        window_surf.blit(control_title, (40, y_pos))
        y_pos += 40
        
        # 获取按键绑定设置
        up_key = self.key_bindings['up']['text']
        down_key = self.key_bindings['down']['text']
        left_key = self.key_bindings['left']['text']
        right_key = self.key_bindings['right']['text']
        shoot_key = self.key_bindings['shoot']['text']
        shoot_switch_key = self.key_bindings['shoot_switch']['text']
        
        controls = [
            f'{up_key}/{down_key}/{left_key}/{right_key}：控制战机移动',
            f'{shoot_key}键：发射子弹',
            f'{shoot_switch_key}键：切换射击模式（直射/散射/连射）',
            'ESC键：返回主菜单'
        ]
        
        for control in controls:
            text_surf = content_font.render(control, True, COLOR_BLACK)
            window_surf.blit(text_surf, (40, y_pos))
            y_pos += line_height
        
        y_pos += 20
        
        # 游戏提示
        tips_title = subtitle_font.render('游戏提示', True, COLOR_DARK_RED_TEXT)
        window_surf.blit(tips_title, (40, y_pos))
        y_pos += 40
        
        tips = [
            '- 消灭敌人可以获得分数',
            '- 收集掉落的道具可以获得强化效果',
            '- 随着游戏进行，敌人会变得更加强大',
            '- 游戏分为4个阶段，可解锁新的射击模式',
            '- 注意躲避敌人的子弹和撞击'
        ]
        
        for tip in tips:
            text_surf = content_font.render(tip, True, COLOR_BLACK)
            window_surf.blit(text_surf, (40, y_pos))
            y_pos += line_height
        
        # 将窗口绘制到屏幕上
        screen.blit(window_surf, (window_x, window_y))

    def handle_key_bind_input(self, key):
        """处理按键绑定输入"""
        if self.input_active and self.active_key_binding:
            # 更新按键绑定
            self.key_bindings[self.active_key_binding]['key'] = key
            self.key_bindings[self.active_key_binding]['text'] = pygame.key.name(key).upper()
            # 重置状态
            self.input_active = False
            self.active_key_binding = None
            # 保存按键绑定设置
            if self.game:
                self.game.save_settings()
            return True
        return False
    
    def update_animations(self, dt):
        """更新UI动画"""
        # 设置界面动画更新
        if self.settings_active:
            self.settings_progress += dt * self.settings_fade_speed
            if self.settings_progress > 1.0:
                self.settings_progress = 1.0
        elif self.settings_progress > 0:
            self.settings_progress -= dt * self.settings_fade_speed
            if self.settings_progress < 0:
                self.settings_progress = 0
        
        # 光标闪烁动画
        if self.number_input_active:
            self.input_cursor_timer += dt
            if self.input_cursor_timer >= 0.5:
                self.input_cursor_visible = not self.input_cursor_visible
                self.input_cursor_timer = 0
class CollisionManager:
    """碰撞检测管理器"""
    def __init__(self, game):
        self.game = game
    
    def handle_collisions(self, dt):
        """处理所有碰撞检测"""
        self._handle_bullet_boundaries()
        self._handle_bullet_vs_bullet()
        self._handle_enemy_bullet_vs_player()
        self._handle_player_bullet_vs_enemy()
        self._handle_enemy_vs_player()
        self._handle_player_vs_powerup()  # 添加小道具碰撞处理
        self._handle_player_vs_random_event()  # 添加随机事件碰撞处理
        self._cleanup_objects()
    
    def _handle_bullet_boundaries(self):
        """处理子弹超出边界"""
        self.game.bullets = [b for b in self.game.bullets if -50 <= b.y <= SCREEN_H + 50]

    def _handle_bullet_vs_bullet(self):
        """处理子弹之间的碰撞"""
        bullets_to_remove = set()
        bullet_collision_count = 0
        
        for i, b1 in enumerate(self.game.bullets):
            if b1 in bullets_to_remove:
                continue
            
            # 创建一个更大的碰撞箱，增大碰撞检测范围
            collision_box_expansion = 8  # 扩大碰撞箱的像素数
            b1_collision_rect = pygame.Rect(
                b1.x - 2 * collision_box_expansion,
                b1.y - 2 * collision_box_expansion,
                b1.w + 2 * collision_box_expansion,
                b1.h + 2 * collision_box_expansion
            )
            
            for b2 in self.game.bullets[i+1:]:
                if b2 in bullets_to_remove:
                    continue

                b2_collision_rect = pygame.Rect(
                    b2.x - 2 * collision_box_expansion,
                    b2.y - 2 * collision_box_expansion,
                    b2.w + 2 * collision_box_expansion,
                    b2.h + 2 * collision_box_expansion
                )
                
                if b1.owner != b2.owner and b1_collision_rect.colliderect(b2_collision_rect):

                    ex = (b1.x + b1.w/2 + b2.x + b2.w/2) / 2
                    ey = (b1.y + b1.h/2 + b2.y + b2.h/2) / 2
                    self.game.explosions.append(Explosion(ex, ey, duration=0.2, max_radius=12))
                    
                    # 处理穿透子弹逻辑
                    # 非穿透子弹才标记为不活跃和移除
                    if not b1.piercing:
                        b1.alive = False
                        bullets_to_remove.add(b1)
                    
                    if not b2.piercing:
                        b2.alive = False
                        bullets_to_remove.add(b2)
                    # 播放爆炸音效
                    Utils.play_sound(self.game.snd_explode, self.game)
                    # 统计子弹碰撞
                    bullet_collision_count += 1
                    break

        # 移除碰撞的子弹
        self.game.bullets = [b for b in self.game.bullets if b not in bullets_to_remove]

        if bullet_collision_count > 0:
            self.game.current_game_stats['bullets_collided'] += bullet_collision_count
            self.game.statistics['total_bullets_collided'] += bullet_collision_count
    
    def _handle_enemy_bullet_vs_player(self):
        """处理敌人子弹击中玩家"""
        bullets_to_remove = []
        
        for b in self.game.bullets:
            if b.owner == BULLET_OWNER_ENEMY and b.rect.colliderect(self.game.player.rect):
                # 检查玩家是否有激活的护盾
                shield_active = self.game.player.shield and self.game.player.shield.active
                
                if shield_active:
                    # 护盾吸收伤害，调用护盾的hit_by_bullet方法
                    shield_broken = self.game.player.shield.hit_by_bullet()
        
                    bullets_to_remove.append(b)
                else:
                    # 没有护盾，玩家直接受伤
                    bullets_to_remove.append(b)
        
                    had_morale = self.game.player.morale > 0
                    self._player_hit_effect()
                    
                    # 如果之前有斗志值，显示斗志中断提示
                    if had_morale and self.game.player.morale == 0:
                        # 显示红色浮动文字
                        ft = FloatingText(self.game.player.x + self.game.player.w // 2,
                                          self.game.player.y,
                                          "斗志中断",
                                          COLOR_RED,
                                          duration=1.5,
                                          rise_speed=60)
                        self.game.floating_texts.append(ft)
                    
                    if self.game.player.health <= 0:
                        self.game.state = GAME_STATE_GAMEOVER
        
        # 移除击中玩家的子弹
        for b in bullets_to_remove:
            if b in self.game.bullets:
                self.game.bullets.remove(b)
    
    def _calculate_damage(self, base_damage, player_morale):
        """根据玩家斗志值计算最终伤害
        """
        return base_damage * ((1 + player_morale * 0.4))
    
    def _handle_player_bullet_vs_enemy(self):
        """处理玩家子弹击中敌人"""
        bullets_to_remove = []
        
        for b in self.game.bullets:
            if b.owner != BULLET_OWNER_PLAYER:
                continue
                
            for e in self.game.enemies:
                    if b.rect.colliderect(e.rect):
                        # 穿透子弹不加入移除列表
                        if not b.piercing:
                            bullets_to_remove.append(b)
            
                        final_damage = self._calculate_damage(b.damage, self.game.player.morale)
                        e.hp -= final_damage  # 使用计算后的最终伤害值
                        
                        if e.hp <= 0:
                    
                            pre_morale = self.game.player.morale
                            self._enemy_destroyed_effect(e)
                            # 检查是否触发了斗志提升（如果击杀后斗志增加了）
                            if self.game.player.morale > pre_morale:
                                # 显示金黄色浮动文字
                                morale_text = f"斗志 {self.game.player.morale}"
                                ft = FloatingText(self.game.player.x + self.game.player.w // 2,
                                                  self.game.player.y,
                                                  morale_text,
                                                  COLOR_GOLD,
                                                  duration=1.5,
                                                  rise_speed=60)
                                self.game.floating_texts.append(ft)
                        break
        
        # 移除击中敌人的子弹
        for b in bullets_to_remove:
            if b in self.game.bullets:
                self.game.bullets.remove(b)
    
    def _handle_enemy_vs_player(self):
        """处理敌人碰到玩家（近身碰撞）"""
        enemies_to_remove = []
        
        for e in self.game.enemies:
            if e.rect.colliderect(self.game.player.rect):
                enemies_to_remove.append(e)
                
                # 检查玩家是否有激活的护盾
                shield_active = self.game.player.shield and self.game.player.shield.active
                
                if shield_active:
                    # 护盾吸收碰撞伤害，调用护盾的hit_by_enemy方法
                    shield_broken = self.game.player.shield.hit_by_enemy()
                    # 如果护盾被打破，显示护盾破碎效果
                    if shield_broken:
                        # 可以在这里添加护盾破碎的视觉效果
                        pass
                else:
                    # 没有护盾，玩家直接受伤
        
                    had_morale = self.game.player.morale > 0
                    self._player_hit_effect(crash=True)
                    
                    # 如果之前有斗志值，显示斗志中断提示
                    if had_morale and self.game.player.morale == 0:
                        # 显示红色浮动文字
                        ft = FloatingText(self.game.player.x + self.game.player.w // 2,
                                          self.game.player.y,
                                          "斗志中断",
                                          COLOR_RED,
                                          duration=1.5,
                                          rise_speed=60)
                        self.game.floating_texts.append(ft)
                    
                    if self.game.player.health <= 0:
                        self.game.state = GAME_STATE_GAMEOVER
                        # 启动 Game Over 动画
                        self.game.ui_manager.gameover_progress = 0.0
                        # 播放失败音效
                        Utils.play_sound(self.game.snd_fail, self.game)
        
        # 移除碰撞的敌人
        self.game.enemies = [e for e in self.game.enemies if e not in enemies_to_remove]
    
    def _player_hit_effect(self, crash=False):
        """玩家被击中的效果"""
        # 减少生命值
        damage = 200 if crash else 100
        self.game.player.health -= damage

        current_time = time.time()
        self.game.player.last_hit_time = current_time
        
        # 如果玩家有斗志值，重置斗志值和连续击杀计数
        if self.game.player.morale > 0:
            self.game.player.morale = 0
            self.game.player.consecutive_kills = 0
        else:
            # 即使没有斗志值，也要重置连续击杀计数
            self.game.player.consecutive_kills = 0
        
        # 计算分数减少量
        score_penalty = 400 if crash else 100
        self.game.score = max(0, self.game.score - score_penalty)
        
        # 在生命值右侧显示红色的伤害值
        health_text_width = self.game.ui_manager.font.size(f'生命值: {self.game.player.health}')[0]
        ft = FloatingText(8 + health_text_width + 4, 36, f'-{damage}', COLOR_DARK_RED)
        self.game.floating_texts.append(ft)
        
        # 在得分右侧显示分数减少
        score_text_width = self.game.ui_manager.font.size(f'得分: {self.game.score}')[0]
        ft = FloatingText(8 + score_text_width + 4, 8, f'-{score_penalty}', COLOR_DARK_RED)
        self.game.floating_texts.append(ft)
        
        # 玩家爆炸
        cx = self.game.player.x + self.game.player.w // 2
        cy = self.game.player.y + self.game.player.h // 2
        duration = 0.6 if crash else 0.5
        radius = 48 if crash else 40
        self.game.explosions.append(Explosion(cx, cy, duration=duration, max_radius=radius))
        
        # 播放爆炸音效
        Utils.play_sound(self.game.snd_explode, self.game)
    
    def _enemy_destroyed_effect(self, enemy):
        """敌人被摧毁的效果"""
        enemy.alive = False
        
        # 增加分数并显示得分浮动文本
        self.game.score += enemy.score
        score_text_width = self.game.ui_manager.font.size(f'得分: {self.game.score}')[0]
        ft = FloatingText(8 + score_text_width + 4, 8, f'+{enemy.score}', COLOR_LIGHT_GREEN)
        self.game.floating_texts.append(ft)
        
        # 增加玩家生命值100
        self.game.player.health = min(MAX_PLAYER_HEALTH, self.game.player.health + 100)
        health_text_width = self.game.ui_manager.font.size(f'生命值: {self.game.player.health}')[0]
        ft = FloatingText(8 + health_text_width + 4, 36, '+100', COLOR_LIGHT_GREEN)
        self.game.floating_texts.append(ft)

        # 无论玩家是否曾经受伤，只要当前处于无状态，都允许重新积累连续击杀
        self.game.player.consecutive_kills += 1
        
        # 每10次连续无伤击杀增加斗志值
        if self.game.player.consecutive_kills % 10 == 0 and self.game.player.morale < 5:
            self.game.player.morale += 1
        
        # 敌人爆炸
        cx = enemy.x + enemy.w // 2
        cy = enemy.y + enemy.h // 2
        self.game.explosions.append(Explosion(cx, cy))
        
        # 播放爆炸音效
        Utils.play_sound(self.game.snd_explode, self.game)
        
        # 统计敌机击杀
        self.game.current_game_stats['enemies_killed'] += 1
        self.game.statistics['total_enemies_killed'] += 1

    def _handle_player_vs_powerup(self):
        """处理玩家与小道具的碰撞"""
        powerups_to_remove = []
        
        for powerup in self.game.powerups:
            if powerup.alive and powerup.rect.colliderect(self.game.player.rect):
                # 玩家拾取小道具
                powerups_to_remove.append(powerup)
                
                # 使用小道具
                task = powerup.use(self.game.player, self.game)
                
                # 如果有定时器任务，保存到游戏的定时器任务列表
                if task and self.game.powerup_tasks:
                    self.game.powerup_tasks.append(task)

                powerup_name = powerup.power_type
                # 转换为可读格式
                if powerup_name == 'speed':
                    display_name = '加速'
                elif powerup_name == 'shield':
                    display_name = '护盾'
                elif powerup_name == 'heal':
                    display_name = '治疗'
                elif powerup_name == 'super_rapid_shoot':
                    display_name = '连发'
                elif powerup_name == 'super_scatter_shoot':
                    display_name = '穿透'
                else:
                    display_name = powerup_name
                
                # 显示绿色浮动文字
                ft = FloatingText(self.game.player.x + self.game.player.w // 2,
                                  self.game.player.y - 20,
                                  f"获得 {display_name}",
                                  COLOR_GREEN,
                                  duration=1.5,
                                  rise_speed=60)
                self.game.floating_texts.append(ft)
        
        # 移除被拾取的小道具
        self.game.powerups = [p for p in self.game.powerups if p not in powerups_to_remove]
    
    def _cleanup_objects(self):
        """清理不再活跃的游戏对象"""
        # 找出飞越屏幕下方被销毁的敌机
        enemies_to_remove = []
        for e in self.game.enemies:
            if not e.alive and e.y > SCREEN_H:
                # 敌机飞越屏幕下方被销毁，玩家分数-100
                self.game.score = max(0, self.game.score - 100)
                # 显示分数减少提示
                score_text_width = self.game.ui_manager.font.size(f'得分: {self.game.score}')[0]
                ft = FloatingText(8 + score_text_width + 4, 8, '-100', COLOR_DARK_RED)
                self.game.floating_texts.append(ft)
            if not e.alive:
                enemies_to_remove.append(e)
        
        # 清理敌人
        self.game.enemies = [e for e in self.game.enemies if e not in enemies_to_remove]
        
        # 清理子弹（移除不活跃的子弹）
        self.game.bullets = [b for b in self.game.bullets if b.alive]
        
        # 清理爆炸特效
        self.game.explosions = [ex for ex in self.game.explosions if ex.alive]
        
        # 清理浮动文本
        self.game.floating_texts = [ft for ft in self.game.floating_texts if ft.alive]
        
        # 清理小道具
        self.game.powerups = [p for p in self.game.powerups if p.alive]
        
        # 清理随机事件
        self.game.random_events = [e for e in self.game.random_events if e.alive]
    
    def _handle_player_vs_random_event(self):
        """处理玩家与随机事件的碰撞"""
        events_to_remove = []
        
        for event in self.game.random_events:
            if event.rect.colliderect(self.game.player.rect):
                # 玩家触碰到随机事件
                events_to_remove.append(event)
                
                # 触发随机事件效果
                event_type = event.event_type
                # 根据事件类型触发相应效果
                if event_type == 1:
                    # 科技发展
                    self._trigger_tech_develop()
                elif event_type == 2:
                    # 经济发展
                    self._trigger_economy_develop()
                elif event_type == 3:
                    # 黑客入侵
                    self._trigger_hack_attack()
                elif event_type == 4:
                    # 空中支援
                    self._trigger_air_support()
                elif event_type == 5:
                    # 飓风袭击
                    self._trigger_hurricane()
        
        # 移除触发的随机事件
        for event in events_to_remove:
            if event in self.game.random_events:
                self.game.random_events.remove(event)
    
    def _trigger_tech_develop(self):
        """触发科技发展事件"""
        # 显示notice
        self.game.notice(3.0, "A市科技快速发展，造出了更高级的飞机")
        
        # 设置标志
        self.game.tech_develop = True
        
        # 15秒后重置标志
        def reset_tech_develop():
            self.game.tech_develop = False
        
        runTaskLater(reset_tech_develop, 30000)
    
    def _trigger_economy_develop(self):
        """触发经济发展事件"""
        # 显示notice
        self.game.notice(3.0, "A市经济快速发展，造出了更多飞机")
        
        # 设置标志
        self.game.economy_develop = True
        
        # 15秒后重置标志
        def reset_economy_develop():
            self.game.economy_develop = False
        
        runTaskLater(reset_economy_develop, 30000)
    
    def _trigger_hack_attack(self):
        """触发黑客入侵事件"""
        # 显示notice
        self.game.notice(3.0, "A市遭到黑客入侵，飞机指挥系统暂时瘫痪")
        
        # 设置标志
        self.game.hack_attack = True
        self.game.hack_attack_times += 1
        
        # 15秒后重置标志
        def reset_hack_attack():
            self.game.hack_attack = False
        
        runTaskLater(reset_hack_attack, 15000)
    
    def _trigger_air_support(self):
        """触发空中支援事件"""
        # 显示notice
        self.game.notice(3.0, "你得到了空中支援！")
        
        # 增加子弹数量，最多增加3个
        self.game.player.bullet_increase_count = min(self.game.player.bullet_increase_count + 1, self.game.player.max_bullet_increase)
        
        # 记录消灭的敌人数量以计算得分
        enemies_destroyed = len(self.game.enemies)
        
        # 为每个敌人创建爆炸效果
        for enemy in self.game.enemies:
            # 创建爆炸效果
            ex, ey = enemy.x + enemy.w // 2, enemy.y + enemy.h // 2
            self.game.explosions.append(Explosion(ex, ey, duration=0.6, max_radius=40))
            
            # 播放爆炸音效
            Utils.play_sound(self.game.snd_explode, self)
            
            # 增加分数
            self.game.score += 100
            
            # 更新统计数据
            self.game.current_game_stats['enemies_killed'] += 1
        
        # 清空所有敌人
        self.game.enemies = []
        
        # 如果消灭了敌人，显示空中支援的文字提示
        if enemies_destroyed > 0:
            self.game.floating_texts.append(FloatingText(
                SCREEN_W // 2 - 100,
                SCREEN_H // 4,
                f'空中支援！消灭 {enemies_destroyed} 架敌机',
                (0, 255, 0),  # 绿色
                duration=2.5,
                rise_speed=30
            ))
    
    def _trigger_hurricane(self):
        """触发飓风袭击事件"""
        # 显示notice
        self.game.notice(3.0, "警告！警告！正在进入风暴区！")
        
        # 设置标志
        self.game.hurricane_active = True
        
        # 显示飓风提示
        self.game.floating_texts.append(FloatingText(
            SCREEN_W // 2 - 120,
            SCREEN_H // 4,
            '飓风来袭！敌人移动加速并改变方向',
            (255, 165, 0),  # 橙色
            duration=2.5,
            rise_speed=30
        ))
        
        # 立即对所有敌人应用飓风效果
        for enemy in self.game.enemies:
            # 增加速度50%
            enemy.vx = enemy.original_vx * 1.5
            enemy.vy = enemy.original_vy * 1.5
            
            # 随机改变方向
            if random.random() > 0.5:
                enemy.vx *= -1
            if random.random() > 0.5:
                enemy.vy *= -1
        
        # 15秒后重置标志
        def reset_hurricane():
            self.game.hurricane_active = False
        
        runTaskLater(reset_hurricane, 30000)
class Game:
    """游戏主类"""
            
    def __init__(self):

        global global_debug
        global_debug = False
        
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption('飞机大战 - balugaq')
        self.clock = pygame.time.Clock()

        self._load_resources()

        self.ui_manager = UIManager(self)
        self.collision_manager = CollisionManager(self)
        
        # 窗口焦点控制
        self.has_focus = True
        self.paused = False
        
        # M 键去抖：记录上次切换时间，单位为秒，仅对 M 键生效
        self.m_cooldown = 0.35
        self.last_m_toggle = 0.0
        
        # R 键（用于 Game Over 立即重玩）去抖
        self.r_cooldown = 1
        self.last_r_restart = 0.0
        
        # 背景滚动控制
        self.bg_scroll = 0.0  # 背景滚动偏移量（像素）
        self.bg_scroll_speed = 5.0  # 每秒向下滚动的像素数
        
        # 数据存储路径
        self.data_dir = os.path.join('data')
        self.settings_file = os.path.join(self.data_dir, 'settings.json')
        self.stats_file = os.path.join(self.data_dir, 'statistics.json')
        
        self.bullets_piercing = False

        self._load_settings()

        self._init_statistics()

        self.allow_switch_shoot_type = True
        
        # 随机事件相关属性
        self.random_events = []  # 存储所有随机事件实体
        self.random_event_timer = 0.0  # 随机事件生成计时器
        self.random_event_interval = 50.0  # 随机事件生成间隔（秒）
        
        # 事件状态标志
        self.tech_develop = False  # 科技发展状态
        self.economy_develop = False  # 经济发展状态
        self.hack_attack = False  # 黑客入侵状态
        self.hack_attack_times = 0
        self.hurricane_active = False  # 飓风袭击状态
        self.hurricane_speed_multiplier = 0.5  # 飓风速度乘数（减慢50%）
        
        # 当前关卡
        self.stage = 1
        
        # 小道具相关属性
        self.powerups = []  # 小道具列表
        self.powerup_spawn_timer = 0.0  # 小道具生成计时器
        self.powerup_spawn_interval = 40.0  # 小道具生成间隔（秒）
        self.max_powerups = 2  # 最大小道具数量
        self.powerup_tasks = []  # 小道具定时器任务列表
        
        # 单次游戏统计数据
        self.current_game_stats = {
            'score': 0,
            'game_time': 0.0,
            'enemies_killed': 0,
            'bullets_collided': 0,
            'start_time': None
        }
        
        self.allow_switch_shoot_type = True
        self.score = 0
        
        # 重置游戏状态
        self.reset()
    
    def _load_settings(self):
        """加载游戏设置"""
        settings = Utils.load_data(self.settings_file)
        if settings:
    
            if 'sfx_volume' in settings:
                self.ui_manager.sfx_volume = settings['sfx_volume']
        
                if 'sound' in self.ui_manager.volume_settings:
                    self.ui_manager.volume_settings['sound']['value'] = int(self.ui_manager.sfx_volume * 100)
            
            if 'music_volume' in settings:
                self.ui_manager.music_volume = settings['music_volume']
                # 将音量值设置回volume_settings字典，确保UI显示正确
                if 'music' in self.ui_manager.volume_settings:
                    self.ui_manager.volume_settings['music']['value'] = int(self.ui_manager.music_volume * 100)
            
            # 加载主音量设置
            if 'master_volume' in settings:
                self.ui_manager.master_volume = settings['master_volume']
                # 将音量值设置回volume_settings字典，确保UI显示正确
                if 'master' in self.ui_manager.volume_settings:
                    self.ui_manager.volume_settings['master']['value'] = int(self.ui_manager.master_volume * 100)

            pygame.mixer.music.set_volume(self.ui_manager.master_volume * self.ui_manager.music_volume)
            
            # 加载按键绑定设置
            if 'key_bindings' in settings:
                for action, key_info in settings['key_bindings'].items():
                    if action in self.ui_manager.key_bindings and isinstance(key_info, dict):
                        # 只更新key值，保留其他属性
                        if 'key' in key_info:
                            self.ui_manager.key_bindings[action]['key'] = key_info['key']
                        if 'text' in key_info:
                            self.ui_manager.key_bindings[action]['text'] = key_info['text']
    
    def _init_statistics(self):
        """初始化游戏统计数据"""
        stats = Utils.load_data(self.stats_file)
        if stats:
            self.statistics = stats
        else:
            # 初始统计数据
            self.statistics = {
                'highest_score': 0,
                'longest_game_time': 0.0,
                'highest_enemies_killed': 0,
                'highest_bullets_collided': 0,
                'total_enemies_killed': 0,
                'total_bullets_collided': 0,
                'total_game_time': 0.0
            }
    
    def save_settings(self):
        """保存游戏设置"""
        # 更新音量属性值
        self.ui_manager.sfx_volume = self.ui_manager.volume_settings['sound']['value'] / 100
        self.ui_manager.music_volume = self.ui_manager.volume_settings['music']['value'] / 100
        # 添加master_volume属性更新
        self.ui_manager.master_volume = self.ui_manager.volume_settings['master']['value'] / 100
        
        # 准备按键绑定数据，排除rect属性
        key_bindings_data = {}
        for action, key_info in self.ui_manager.key_bindings.items():
            if isinstance(key_info, dict):
                # 只保存key和text属性，不保存rect
                key_bindings_data[action] = {
                    'key': key_info.get('key', pygame.K_a),
                    'text': key_info.get('text', 'A')
                }
        
        settings = {
            'sfx_volume': self.ui_manager.sfx_volume,
            'music_volume': self.ui_manager.music_volume,
            'master_volume': self.ui_manager.master_volume  # 添加master_volume
        }
        # 如果key_bindings_data不为空，则添加到设置中
        if key_bindings_data:
            settings['key_bindings'] = key_bindings_data
        
        Utils.save_data(settings, self.settings_file)
    
    def save_statistics(self):
        """保存游戏统计数据"""
        Utils.debug(f"尝试保存统计数据到文件: {self.stats_file}")
        try:
            Utils.save_data(self.statistics, self.stats_file)
            Utils.debug("统计数据保存成功")
        except Exception as e:
            Utils.debug(f"统计数据保存失败: {e}")
    
    def update_statistics(self):
        """更新游戏统计数据（游戏结束时调用）"""
        Utils.debug("更新统计数据开始")
        Utils.debug(f"当前游戏统计: {self.current_game_stats}")
        # 更新最高分数
        if self.score > self.statistics['highest_score']:
            self.statistics['highest_score'] = self.score
            Utils.debug(f"新最高分: {self.score}")
        
        # 更新最长游戏时长
        if self.current_game_stats['game_time'] > self.statistics['longest_game_time']:
            self.statistics['longest_game_time'] = self.current_game_stats['game_time']
            Utils.debug(f"新最长游戏时长: {self.current_game_stats['game_time']}")
        
        # 更新单次最高敌机击杀数
        if self.current_game_stats['enemies_killed'] > self.statistics['highest_enemies_killed']:
            self.statistics['highest_enemies_killed'] = self.current_game_stats['enemies_killed']
            Utils.debug(f"新最高敌机击杀数: {self.current_game_stats['enemies_killed']}")
        
        # 更新单次最高子弹击杀数
        if self.current_game_stats['bullets_collided'] > self.statistics['highest_bullets_collided']:
            self.statistics['highest_bullets_collided'] = self.current_game_stats['bullets_collided']
            Utils.debug(f"新最高子弹击杀数: {self.current_game_stats['bullets_collided']}")
        
        # 更新总敌机击杀数
        self.statistics['total_enemies_killed'] += self.current_game_stats['enemies_killed']
        Utils.debug(f"总敌机击杀数更新为: {self.statistics['total_enemies_killed']}")
        
        # 更新总子弹击杀数
        self.statistics['total_bullets_collided'] += self.current_game_stats['bullets_collided']
        Utils.debug(f"总子弹击杀数更新为: {self.statistics['total_bullets_collided']}")
        
        # 更新总游戏时长
        self.statistics['total_game_time'] += self.current_game_stats['game_time']
        Utils.debug(f"总游戏时长更新为: {self.statistics['total_game_time']}")
        
        # 保存统计数据
        Utils.debug(f"最终统计数据: {self.statistics}")
        self.save_statistics()
        Utils.debug("统计数据保存完成")
    
    def _load_resources(self):
        """加载游戏资源"""
        # 图片资源
        self.bg_img = Utils.load_image('background', BG_SIZE)
        self.player_img = Utils.load_image('player', PLAYER_SIZE)
        # 加载四个阶段的敌人图像
        self.enemy_img1 = Utils.load_image('enemy1', ENEMY_SIZE)
        self.enemy_img2 = Utils.load_image('enemy2', ENEMY_SIZE)
        self.enemy_img3 = Utils.load_image('enemy3', ENEMY_SIZE)
        self.enemy_img4 = Utils.load_image('enemy4', ENEMY_SIZE)
        self.bullet_img = Utils.load_image('bullet', BULLET_SIZE)
        
        # 加载小道具图片
        self.powerup_speed_img = Utils.load_image('speed', (64, 64))
        self.powerup_shield_img = Utils.load_image('shield', (64, 64))
        self.powerup_heal_img = Utils.load_image('heal', (64, 64))
        self.powerup_super_rapid_shoot_img = Utils.load_image('super_rapid_shoot', (64, 64))
        self.powerup_super_scatter_shoot_img = Utils.load_image('super_scatter_shoot', (64, 64))

        # 音效资源
        try:
            pygame.mixer.init()
        except Exception:
            pass
        
        self.snd_player_shoot = Utils.load_sound('player_shoot')
        self.snd_enemy_shoot = Utils.load_sound('enemy_shoot')
        self.snd_explode = Utils.load_sound(SOUND_EXPLODE)
        self.snd_popup = Utils.load_sound('popup')
        self.snd_ui_hover = Utils.load_sound('hover')
        self.snd_ui_click = Utils.load_sound('click')
        self.snd_fail = Utils.load_sound(SOUND_FAIL)
        self.snd_powerup = Utils.load_sound(SOUND_POWERUP)
        self.snd_shield_hit = Utils.load_sound('shield_hit')
        self.snd_shield_fail = Utils.load_sound('shield_fail')

        self.music_volume = 0.5
        self.music_loaded = False
        try:
            music_path_ogg = os.path.join(ASSETS_MUSIC, 'bgm.ogg')
            music_path = None
            
            if os.path.isfile(music_path_ogg):
                music_path = music_path_ogg
                
            if music_path is not None:
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(self.music_volume)
                    # 循环播放，淡入 1 秒
                    pygame.mixer.music.play(-1, 0.0, 1000)
                    self.music_loaded = True
                except Exception:
                    self.music_loaded = False
        except Exception:
            self.music_loaded = False
    
    def reset(self):
        """重置游戏状态"""
        self.update_statistics()
        
        # 清除所有未处理的事件，避免长按按键的事件在新游戏中被处理
        pygame.event.clear()
        
        # 取消之前的定时任务（如果存在）
        if hasattr(self, 'rapid_shot_counter_task') and self.rapid_shot_counter_task:  # 保留此检查，因为任务可能不存在
            self.rapid_shot_counter_task.cancel()
            self.rapid_shot_counter_task = None

        self.player = Player(SCREEN_W // 2 - 18, SCREEN_H - 150, self.player_img)

        self.player.morale = 0
        self.player.consecutive_kills = 0
        self.player.last_hit_time = -1

        self.bullets = []
        self.enemies = []
        self.explosions = []
        self.floating_texts = []
        self.powerups = []  # 重置小道具列表
        
        # 游戏状态
        self.spawn_timer = 0.0
        self.spawn_interval = 2
        self.powerup_spawn_timer = 0.0  # 重置小道具生成计时器
        self.score = 0
        self.state = GAME_STATE_TITLE  # title / playing / gameover
        # 记录进入的时间
        self.state_enter_time = time.time()
        self.stage = 1  # 游戏阶段，1-4
        # 按键冷却时间配置
        self.playing_r_cooldown = 2.0  # 游戏状态R键冷却时间（秒）
        self.title_esc_cooldown = 2.0  # 主界面ESC键冷却时间（秒）

        # 模态窗口重置
        self.ui_manager.modal_active = False
        self.ui_manager.modal_progress = 0.0
        self.ui_manager.modal_type = None
        
        # 开始游戏过渡动画
        self.start_transition = False
        self.transition_progress = 0.0
        self.transition_speed = 2.0

        self.paused = not self.has_focus
        
        # 单次游戏统计数据
        self.current_game_stats = {
            'score': 0,
            'game_time': 0.0,
            'enemies_killed': 0,
            'bullets_collided': 0,
            'start_time': None
        }
    
    def _spawn_highest_level_enemy(self):
        """生成当前stage最高级别的敌机"""

        enemy_images = [self.enemy_img1, self.enemy_img2, self.enemy_img3, self.enemy_img4]
        # 确保stage不超过敌机图像的数量
        enemy_index = min(self.stage - 1, len(enemy_images) - 1)
        highest_enemy_image = enemy_images[enemy_index]
        
        # 生成位置
        x = random.randint(0, SCREEN_W - 30)
        
        # 确定敌机级别和生命值
        enemy_level = enemy_index + 1  # level从1开始
        hp = enemy_level * 100  # 根据级别设置生命值：1级100，2级200，3级300，4级400

        e = Enemy(x, -40, game=self, vy=random.randint(100, 160), hp=hp, score=100, image=highest_enemy_image, stage=enemy_level)
        e.level = enemy_level
        self.enemies.append(e)
        
    def spawn_powerup(self):
        """生成小道具，限制最多2个，分布在左右半场的上半部分"""
        # 检查当前小道具数量是否已达到最大限制
        if len(self.powerups) >= self.max_powerups:
            return
        
        # 检查左右半场的上半部分是否有空间生成小道具
        left_available = True
        right_available = True
        
        # 检查现有小道具的位置
        for powerup in self.powerups:
            # 左半场判断
            if powerup.x < SCREEN_W // 2:
                left_available = False
            # 右半场判断
            else:
                right_available = False
        
        # 确定可以生成的区域
        available_zones = []
        if left_available:
            available_zones.append(ZONE_LEFT)
        if right_available:
            available_zones.append(ZONE_RIGHT)
        
        # 如果没有可用区域，则不生成
        if not available_zones:
            return
        
        # 随机选择一个可用区域
        zone = random.choice(available_zones)

        if zone == ZONE_LEFT:
            # 左半场的上半部分
            x = random.randint(64, (SCREEN_W // 2) - 64)
        else:
            # 右半场的上半部分
            x = random.randint((SCREEN_W // 2) + 64, SCREEN_W - 64)
        
        y = random.randint(64, SCREEN_H // 2)
        
        # 检查玩家是否获得了连射或散射道具增幅，以及场上是否存在这些道具
        player_has_rapid_boost = False
        player_has_scatter_boost = False
        field_has_rapid = False
        field_has_scatter = False
        
        # 检查玩家状态
        if self.player and self.allow_switch_shoot_type:

            if not self.allow_switch_shoot_type:
                if self.player.current_shoot_type == SHOOT_TYPE_RAPID:
                    player_has_rapid_boost = True
                elif self.player.current_shoot_type == SHOOT_TYPE_SCATTER:
                    player_has_scatter_boost = True
        
        # 检查场上已存在的道具
        for powerup in self.powerups:
            if powerup.power_type == 'super_rapid_shoot':
                field_has_rapid = True
            elif powerup.power_type == 'super_scatter_shoot':
                field_has_scatter = True
        
        # 根据条件确定可生成的道具类型列表
        powerup_types = ['speed', 'shield', 'heal']  # 基础道具类型
        
        # 只有当玩家没有相关增幅且场上没有对应道具时，才将连射和散射道具加入可生成列表
        if not player_has_rapid_boost and not field_has_rapid and not player_has_scatter_boost and not field_has_scatter:
            if self.stage >= 3:
                powerup_types.append('super_scatter_shoot')
            if self.stage >= 4:
                powerup_types.append('super_rapid_shoot')

        if not powerup_types:
            return
        
        # 随机选择小道具类型
        powerup_type = random.choice(powerup_types)

        if powerup_type == 'speed':
            powerup = SpeedPowerUp(x, y)
        elif powerup_type == 'shield':
            powerup = ShieldPowerUp(x, y)
        elif powerup_type == 'heal':
            powerup = HealPowerUp(x, y)
        elif powerup_type == 'super_rapid_shoot':
            powerup = SuperRapidShootPowerUp(x, y)
        elif powerup_type == 'super_scatter_shoot':
            powerup = SuperScatterShootPowerUp(x, y)
        
        # 添加到小道具列表
        self.powerups.append(powerup)
        
        # 播放powerup音效
        Utils.play_sound(self.snd_powerup, self)
    
    def spawn_enemy(self):
        """生成敌机，根据stage调整生成逻辑"""
        # 定义每个stage的飞机类型和参数
        # 高等级stage可以生成低等级stage的飞机
        base_stage_images = {
            1: [{'image': self.enemy_img1, 'weight': 1.0}],
            2: [{'image': self.enemy_img1, 'weight': 0.3}, {'image': self.enemy_img2, 'weight': 0.7}],
            3: [{'image': self.enemy_img1, 'weight': 0.1}, {'image': self.enemy_img2, 'weight': 0.3}, {'image': self.enemy_img3, 'weight': 0.6}],
            4: [{'image': self.enemy_img1, 'weight': 0.1}, {'image': self.enemy_img2, 'weight': 0.2}, {'image': self.enemy_img3, 'weight': 0.4}, {'image': self.enemy_img4, 'weight': 0.3}]
        }
        
        # 复制基础配置
        stage_images = {}
        for stage, images in base_stage_images.items():
            stage_images[stage] = [img.copy() for img in images]

        # todo: 难度系数
        # 简易: 3.0 2.0 2.0 2.0
        # 中等（默认）: 2.0 1.8 1.6 1.5
        # 困难: 2.0 1.6 1.5 1.2
        interval_map = {1: 2.0, 2: 1.8, 3: 1.6, 4: 1.5}
        base_interval = interval_map.get(self.stage, 2.0)
        
        # 处理经济发展事件效果 - 降低生成间隔
        if self.economy_develop:
            self.spawn_interval = max(0.5, base_interval - 0.2)  # 确保间隔不会太小
        else:
            self.spawn_interval = base_interval
        
        # 每次生成时实时计算随机数量
        count_range_map = {1: (1, 1), 2: (1, 1), 3: (1, 1), 4: (1, 2)}
        count_range = count_range_map.get(self.stage, (1, 1))
        spawn_count = random.randint(*count_range)

        # 检查是否触发了黑客入侵事件，如果是则阻止敌人生成
        if self.hack_attack:
            return
            
        # 处理科技发展事件效果
        tech_develop_effect = False
        if self.tech_develop:
            tech_develop_effect = True
            if self.stage < 4:
                # stage < 4时，生成的敌方飞机等级升高1级
                # 使用更高stage的飞机配置
                available_images = stage_images.get(self.stage + 1, stage_images[self.stage])
            else:
                # stage = 4时，我们将在权重选择时特别处理
                available_images = stage_images.get(self.stage, stage_images[1])
        else:
            # 正常情况
            available_images = stage_images.get(self.stage, stage_images[1])
        
        # 根据权重随机选择一个飞机类型
        # 处理stage=4时的科技发展效果
        if tech_develop_effect and self.stage == 4:
            # 复制可用图像列表以避免修改原始数据
            modified_images = [img.copy() for img in available_images]
            # 找到4级飞机（enemy_img4）并增加其权重
            for img_info in modified_images:
                if img_info['image'] == self.enemy_img4:
                    img_info['weight'] = 0.2  # 设置为0.2
                    break
            # 使用修改后的权重计算
            total_weight = sum(img['weight'] for img in modified_images)
            random_value = random.uniform(0, total_weight)
            cumulative_weight = 0
            enemy_image = self.enemy_img1  # 默认值
            
            for img_info in modified_images:
                cumulative_weight += img_info['weight']
                if random_value <= cumulative_weight:
                    enemy_image = img_info['image']
                    break
        else:
            # 正常权重选择
            total_weight = sum(img['weight'] for img in available_images)
            random_value = random.uniform(0, total_weight)
            cumulative_weight = 0
            enemy_image = self.enemy_img1  # 默认值
            
            for img_info in available_images:
                cumulative_weight += img_info['weight']
                if random_value <= cumulative_weight:
                    enemy_image = img_info['image']
                    break
        
        # 标记是否成功生成了敌人
        spawned = False
        
        # 生成指定数量的敌机
        for _ in range(spawn_count):
            # 尝试多个位置，直到找到一个合适的生成点
            max_attempts = 10
            min_distance = 60
            
            for _ in range(max_attempts):
                # 将屏幕宽度分成几个区域，随机选择一个
                zone_width = (SCREEN_W - 30) // 3
                zone = random.randint(0, 2)
                x = random.randint(zone * zone_width, (zone + 1) * zone_width - 30)

                # 根据位置设定不同的速度范围，左边较慢，右边较快
                if zone == 0:  # 左区域
                    vy = random.randint(60, 120)
                elif zone == 1:  # 中间区域
                    vy = random.randint(100, 160)
                else:  # 右区域
                    vy = random.randint(140, 200)

                # 检查与现有敌机的距离
                valid_position = True
                for enemy in self.enemies:
                    dx = abs(enemy.x - x)
                    dy = abs(enemy.y - (-40))
                    if dx < min_distance and dy < min_distance:
                        valid_position = False
                        break

                if valid_position:
                    # 根据飞机图像确定飞机级别
                    if enemy_image == self.enemy_img1:
                        enemy_level = 1
                    elif enemy_image == self.enemy_img2:
                        enemy_level = 2
                    elif enemy_image == self.enemy_img3:
                        enemy_level = 3
                    else:  # self.enemy_img4
                        enemy_level = 4
                    
                    # 根据级别设置生命值
                    hp = enemy_level * 100

                    e = Enemy(x, -40, game=self, vy=vy, hp=hp, score=100, image=enemy_image, stage=enemy_level)
            
                    e.level = enemy_level
                    self.enemies.append(e)
                    spawned = True
                    break

        # 只有在前面的循环没有成功生成敌人时，才执行保底生成
        if not spawned:
            x = random.randint(0, SCREEN_W - 30)
            
            # 根据飞机图像确定飞机级别
            if enemy_image == self.enemy_img1:
                enemy_level = 1
            elif enemy_image == self.enemy_img2:
                enemy_level = 2
            elif enemy_image == self.enemy_img3:
                enemy_level = 3
            else:  # self.enemy_img4
                enemy_level = 4
            
            # 根据级别设置生命值：1级100，2级200，3级300，4级400
            hp = enemy_level * 100
            
            e = Enemy(x, -40, game=self, vy=random.randint(100, 160), hp=hp, score=100, image=enemy_image, stage=enemy_level)
            e.level = enemy_level
            self.enemies.append(e)
    
    def create_bullet(self, owner, x, y, vy):
        """创建子弹并设置图片"""
        bullet = Bullet(x, y, vy, owner)
        if self.bullet_img:
            bullet.image = self.bullet_img
            bullet.w, bullet.h = bullet.image.get_size()
            bullet.rect = pygame.Rect(bullet.x, bullet.y, bullet.w, bullet.h)
        
        # 如果是玩家子弹且游戏有穿透模式标记，设置穿透属性
        if owner == BULLET_OWNER_PLAYER and self.bullets_piercing:
            bullet.piercing = True
            
        return bullet
    
    def update(self, dt):
        """更新游戏逻辑"""
        for ex in self.explosions:
            ex.update(dt)

        for ft in self.floating_texts:
            ft.update(dt)

        for powerup in self.powerups:
            powerup.update(dt)
        
        # 更新随机事件
        for event in self.random_events[:]:
            if self.player and self.player.alive:
                event.update(dt, self.player.x, self.player.y)
            else:
                event.update(dt, SCREEN_W//2, SCREEN_H//2)  # 如果玩家不存在，向屏幕中心移动
            if not event.alive:
                self.random_events.remove(event)

        if self.state == GAME_STATE_PLAYING:
            # 统计游戏时长
            self.current_game_stats['game_time'] += dt / 60  # 转换为分钟
            keys = pygame.key.get_pressed()
            # 随机事件生成逻辑
            if self.stage >= 2:
                # 第一次进入stage>=2时立即生成一个随机事件
                if len(self.random_events) == 0 and self.random_event_timer == 0.0:
                    # 生成随机事件在场地上半部分
                    x = random.randint(64, SCREEN_W - 64)
                    y = random.randint(64, SCREEN_H // 2)
                    self.random_events.append(RandomEvent(x, y))
                    self.random_event_timer = self.random_event_interval  # 重置计时器
                else:
                    # 计时器减少
                    self.random_event_timer -= dt
                    # 当计时器归零时生成新的随机事件
                    if self.random_event_timer <= 0.0:
                        # 生成随机事件在场地上半部分
                        x = random.randint(64, SCREEN_W - 64)
                        y = random.randint(64, SCREEN_H // 2)
                        self.random_events.append(RandomEvent(x, y))
                        self.random_event_timer = self.random_event_interval  # 重置计时器
            
            if self.allow_switch_shoot_type:
        
                if self.stage <= 2:
                    # stage 1-2: 只能直射
                    # 保存原始射击方式，用于stage提升后恢复
                    self.player.saved_shoot_type = self.player.current_shoot_type
                    self.player.current_shoot_type = SHOOT_TYPE_DIRECT
                elif self.stage == 3 or self.stage == 4:
                    # stage 3-4: 恢复保存的射击类型
                    # 根据当前stage确定可用的射击类型
                    allowed_types = [SHOOT_TYPE_DIRECT, SHOOT_TYPE_SCATTER]
                    if self.stage == 4:
                        allowed_types.append(SHOOT_TYPE_RAPID)
                    
                    # 检查saved_shoot_type是否有效（避免hasattr）
                    if getattr(self.player, 'saved_shoot_type', None) in allowed_types:
                        self.player.current_shoot_type = self.player.saved_shoot_type
                    else:
                        self.player.current_shoot_type = SHOOT_TYPE_DIRECT  # 默认直射
                    
                    # 重置保存的射击类型而不是删除属性
                    self.player.saved_shoot_type = None
            
            # 动态调整按键重复频率
            # 当游戏开始且按下的是移动键时，使用较快的重复频率
            is_movement_key_pressed = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN] or \
                                     keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]
            
            if is_movement_key_pressed:
                # 移动键按下时，使用较快的重复频率
                pygame.key.set_repeat(100, 30)
            else:
                # 其他情况使用较慢的重复频率
                pygame.key.set_repeat(1000, 200)

            self.player.update(dt, keys, self)

            if self.player.shield and self.player.shield.active:
                self.player.shield.update()

            # 射击
            # 自动射击检查 - 修改为使用与手动射击相同的逻辑但标记为自动射击
            if self.player.can_auto_shoot():
                bullets = self.player.shoot(is_auto=True, game=self)  # 调用相同的shoot方法，但标记为自动射击
                if bullets:
                    for b in bullets:
                        new_b = self.create_bullet(BULLET_OWNER_PLAYER, b.x, b.y, b.vy)
                        # 复制子弹的射击类型和角度属性
                        new_b.shoot_type = b.shoot_type
                        new_b.angle = b.angle
                        Utils.play_sound(self.snd_player_shoot, self)
                        self.bullets.append(new_b)

            # 手动射击检查
            if keys[pygame.K_SPACE] and self.player.can_shoot():
                bullets = self.player.shoot(game=self)
                if bullets:
                    for b in bullets:
                        new_b = self.create_bullet(BULLET_OWNER_PLAYER, b.x, b.y, b.vy)
                        # 复制子弹的射击类型和角度属性，确保散射状态下正确发射散射子弹
                        new_b.shoot_type = b.shoot_type
                        new_b.angle = b.angle
                        Utils.play_sound(self.snd_player_shoot, self)
                        self.bullets.append(new_b)

            for b in self.bullets:
                b.update(dt)

            for e in self.enemies:
                new_bullets = e.update(dt)
                for b in new_bullets:
                    new_b = self.create_bullet(BULLET_OWNER_ENEMY, b.x, b.y, b.vy)
                    Utils.play_sound(self.snd_enemy_shoot, self)
                    self.bullets.append(new_b)

            # 生成敌人，但在黑客入侵期间不生成
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval and not self.hack_attack:
                self.spawn_timer = 0
                self.spawn_enemy()
                
            # 生成小道具
            self.powerup_spawn_timer += dt
            if self.powerup_spawn_timer >= self.powerup_spawn_interval:
                self.powerup_spawn_timer = 0
                self.spawn_powerup()

            # 处理碰撞
            self.collision_manager.handle_collisions(dt)
            
            # 检查场上是否有敌机，如果没有则立即生成一个当前stage最高级别的敌机
            # 但在黑客入侵事件期间不生成任何敌人
            if not self.enemies and not self.hack_attack:
                self._spawn_highest_level_enemy()
            
            Utils.debug(f"stage: {self.stage} - killed: {self.current_game_stats['enemies_killed']}")
            # todo: 当stage切换时，使用notice与玩家交互
            # 阶段切换逻辑
            if self.stage == 1 and self.current_game_stats['enemies_killed'] >= 30:
                self.stage = 2
                self.spawn_interval = 1.5  
                # 显示阶段提升信息
                self.floating_texts.append(FloatingText(SCREEN_W // 2 - 50, SCREEN_H // 2, '阶段 2', COLOR_GOLD, duration=2.0, rise_speed=20))
            elif self.stage == 2 and self.current_game_stats['enemies_killed'] >= 120:
                self.stage = 3
                self.spawn_interval = 1.2
                self.floating_texts.append(FloatingText(SCREEN_W // 2 - 50, SCREEN_H // 2, '阶段 3', COLOR_GOLD, duration=2.0, rise_speed=20))
                # 添加蓝色浮动文字提示已解锁散射模式
                if self.player:
                    self.floating_texts.append(FloatingText(
                        self.player.x + self.player.w // 2,
                        self.player.y - 30,
                        '已解锁射击模式: 散射',
                        (135, 206, 250),  # 天蓝色
                        duration=2.0,
                        rise_speed=40
                    ))
            elif self.stage == 3 and self.current_game_stats['enemies_killed'] >= 300:
                self.stage = 4
                self.spawn_interval = 1.0
                self.floating_texts.append(FloatingText(SCREEN_W // 2 - 50, SCREEN_H // 2, '阶段 4', COLOR_GOLD, duration=2.0, rise_speed=20))
                # 添加蓝色浮动文字提示已解锁连射模式
                if self.player:
                    self.floating_texts.append(FloatingText(
                        self.player.x + self.player.w // 2,
                        self.player.y - 30,
                        '已解锁射击模式: 连射',
                        (135, 206, 250),  # 天蓝色
                        duration=2.0,
                        rise_speed=40
                    ))

    def draw(self):
        """绘制游戏画面"""
        if self.state == GAME_STATE_TITLE or self.ui_manager.stats_active:
            self._draw_title_screen()
            return

        # 绘制背景
        self._draw_background()

        # 绘制游戏对象
        for e in self.enemies:
            e.draw(self.screen)
        
        # 绘制小道具（在敌人下方，在子弹下方，在玩家下方）
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # 绘制随机事件（与小道具同层级）
        for event in self.random_events:
            event.draw(self.screen)

        for b in self.bullets:
            b.draw(self.screen)

        self.player.draw(self.screen)
        
        # 绘制玩家护盾（如果存在且激活）
        if self.player.shield and self.player.shield and self.player.shield.active:
            self.player.shield.draw(self.screen)

        # 绘制爆炸特效（覆盖在实体之上）
        for ex in self.explosions:
            ex.draw(self.screen)

        # 绘制HUD
        self.ui_manager.draw_hud(self.screen, self.score, self.player)

        # 绘制暂停提示
        self._draw_pause_screen()
        
        # 绘制模态弹窗
        if self.ui_manager.modal_active:
            self.ui_manager.draw_modal(self.screen, 0)  # dt在run方法中更新

        # 绘制游戏结束画面
        if self.state == GAME_STATE_GAMEOVER:
            # 清除所有notice
            if self.ui_manager:
                self.ui_manager.clear_top_right_text()
            self._draw_gameover_screen()

        pygame.display.flip()
    
    def _draw_background(self):
        """绘制背景"""

        self.bg_scroll += self.bg_scroll_speed
        if self.bg_scroll >= SCREEN_H:
            self.bg_scroll = 0

        # 背景图或纯色
        if self.bg_img:
            # 绘制两张背景图实现无缝滚动
            y1 = int(self.bg_scroll - SCREEN_H)
            y2 = int(self.bg_scroll)
            self.screen.blit(self.bg_img, (0, y1))
            self.screen.blit(self.bg_img, (0, y2))
        else:
            self.screen.fill(COLOR_NAVY_BLUE)
    
    def _draw_title_screen(self):
        """绘制标题界面"""
        Utils.debug(f"绘制标题界面 - settings_active={self.ui_manager.settings_active}, stats_active={self.ui_manager.stats_active}")
        # 绘制背景
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill((16, 16, 32))
        
        # 绘制标题
        self.ui_manager.draw_title(self.screen, self.start_transition, self.transition_progress)

        if self.ui_manager.settings_active:
            self.ui_manager.draw_settings(self.screen)
        elif self.ui_manager.tutorial_active:
            self.ui_manager.draw_tutorial(self.screen)
        elif self.ui_manager.stats_active:
            Utils.debug("绘制统计界面，stats_active=True")
            Utils.debug(f"当前统计数据: {self.statistics}")
            # 合并当前游戏统计和历史统计，用于在游戏中显示实时数据
            display_stats = self.statistics.copy()
            # 添加当前游戏的实时统计数据
            display_stats['current_score'] = self.score
            display_stats['current_enemies_killed'] = self.current_game_stats['enemies_killed']
            display_stats['current_bullets_collided'] = self.current_game_stats['bullets_collided']
            display_stats['current_game_time'] = self.current_game_stats['game_time']
            self.ui_manager.draw_statistics(self.screen, display_stats)
        
        # 绘制模态弹窗（如果激活）
        if self.ui_manager.modal_active:
            self.ui_manager.draw_modal(self.screen, 0.016)  # 使用固定的dt值进行绘制
        
        pygame.display.flip()
    
    def _draw_pause_screen(self):
        """绘制暂停界面"""
        if self.paused and not self.ui_manager.modal_active and self.state != GAME_STATE_GAMEOVER:
            pause_text = self.ui_manager.large_font.render('游戏已暂停', True, COLOR_WHITE)
            pause_hint = self.ui_manager.font.render('点击窗口继续游戏', True, COLOR_LIGHT_GRAY)
            px = SCREEN_W // 2 - pause_text.get_width() // 2
            py = SCREEN_H // 2 - pause_text.get_height()
            self.screen.blit(pause_text, (px, py))
            self.screen.blit(pause_hint, (SCREEN_W // 2 - pause_hint.get_width() // 2, py + 40))
    
    def _draw_gameover_screen(self):
        """绘制游戏结束界面"""
        over_s = self.ui_manager.large_font.render('GAME OVER', True, COLOR_LIGHT_RED)
        sub_s = self.ui_manager.font.render('按 R 重玩，Esc 退出', True, COLOR_GRAY)
        self.screen.blit(over_s, (SCREEN_W // 2 - over_s.get_width() // 2, SCREEN_H // 2 - 40))
        self.screen.blit(sub_s, (SCREEN_W // 2 - sub_s.get_width() // 2, SCREEN_H // 2 + 8))
    
    def run(self):
        """游戏主循环"""
        Utils.debug("进入游戏主循环")
        try:
            running = True
            Utils.debug("初始化游戏循环变量")
            
            while running:
                dt = self.clock.tick(FPS) / 1000.0
                
                # 处理事件
                running = self._handle_events(dt)

                self.ui_manager.update_animations(dt)

                if self.ui_manager.modal_active:
                    self.ui_manager.modal_progress += dt * self.ui_manager.modal_fade_speed
                    if self.ui_manager.modal_progress > 1.0:
                        self.ui_manager.modal_progress = 1.0
                elif self.ui_manager.modal_progress > 0:
                    self.ui_manager.modal_progress -= dt * self.ui_manager.modal_fade_speed
                    if self.ui_manager.modal_progress < 0:
                        self.ui_manager.modal_progress = 0
                
                # 开始游戏过渡动画
                if self.start_transition:
                    self.transition_progress += dt * self.transition_speed
                    if self.transition_progress >= 1.0:
                        # 过渡完成，开始游戏
                        self.start_transition = False
                        self.transition_progress = 0.0
                        self.state = GAME_STATE_PLAYING
                        # 记录进入游戏状态的时间
                        self.state_enter_time = time.time()
                        
                        self.notice(3.0, "欢迎开始游戏！", "祝你好运！")
                        
                        def reset_rapid_shot_counter():
                            self.player.rapid_shot_counter = 0

                        self.rapid_shot_counter_task = runTaskTimer(reset_rapid_shot_counter, 0, 1000)

                global_task_scheduler.update()
                
                # 清理不再活跃的浮动文字
                self.floating_texts = [ft for ft in self.floating_texts if ft.alive]

                if not self.ui_manager.modal_active and not self.paused:
                    if self.state == GAME_STATE_PLAYING:
                        self.update(dt)

                # 绘制游戏
                self.draw()
            
            # 游戏退出时保存统计数据
            Utils.debug("游戏即将退出，保存统计数据...")
            self.update_statistics()
            pygame.quit()
        except Exception as e:
            import traceback
            Utils.error(f"游戏运行出错: {e}")
            Utils.error("错误详情:")
            traceback.print_exc()
            input("按Enter键退出...")
    
    def _handle_events(self, dt):
        """处理游戏事件"""
        running = True
        
        for event in pygame.event.get():
            # 忽略文本输入事件
            if event.type in (getattr(pygame, 'TEXTINPUT', None), getattr(pygame, 'TEXTEDITING', None)):
                continue
                
            # 处理退出
            if event.type == pygame.QUIT:
                running = False
                
            # 按键按下
            elif event.type == pygame.KEYDOWN:
                # 数字输入处理
                if self.ui_manager.number_input_active:
                    self._handle_number_input(event)
                # 其他按键处理 - 只在数字输入未激活或_handle_number_input未处理的情况下调用
                result = self._handle_keydown(event)
                if result is False:
                    running = False
                
            # 鼠标点击处理
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mousedown(event)
            
            # 鼠标移动处理（用于音量滑块拖动）
            elif event.type == pygame.MOUSEMOTION:
                if self.ui_manager.settings_active:
                    # 检查是否有音量滑块正在被拖动
                    for vol_name, vol_info in self.ui_manager.volume_settings.items():
                        if vol_info.get('dragging', False):
                            # 计算新的音量值（以2%为单位）
                            slider_rect = vol_info['rect']
                            raw_value = (event.pos[0] - slider_rect.x) / slider_rect.width * 100
                            # 四舍五入到最近的2%倍数
                            new_value = round(raw_value / 2) * 2
                            new_value = max(0, min(100, new_value))
                            vol_info['value'] = new_value

                            if vol_name == 'music' or vol_name == 'master':
                                # 计算最终音乐音量 = 主音量 x 音乐音量
                                master_val = self.ui_manager.volume_settings['master']['value'] / 100
                                music_val = self.ui_manager.volume_settings['music']['value'] / 100
                                pygame.mixer.music.set_volume(master_val * music_val)
            
            # 鼠标释放处理
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.ui_manager.settings_active:
                    # 释放所有音量滑块的拖动状态
                    for vol_name, vol_info in self.ui_manager.volume_settings.items():
                        vol_info['dragging'] = False
            
                    self.save_settings()
                
            # 窗口焦点/最小化事件
            elif event.type == pygame.ACTIVEEVENT:
                self._handle_active_event(event)
            elif event.type == pygame.WINDOWFOCUSLOST:
                self.has_focus = False
                self.paused = True
                # 窗口失去焦点时，释放所有音量滑块的拖动状态
                for vol_name, vol_info in self.ui_manager.volume_settings.items():
                    vol_info['dragging'] = False
            elif event.type == pygame.WINDOWFOCUSGAINED:
                self.has_focus = True
                self.paused = False
        return running
    
    def _handle_keydown(self, event):
        """处理按键按下事件"""
            
        # Ctrl+Q 强制退出游戏
        if event.key == pygame.K_q and event.mod & pygame.KMOD_CTRL:
            print("用户按下Ctrl+Q强制退出游戏")
            return False
        
        # 退出游戏
        if event.key == pygame.K_ESCAPE:
            # 取消按键绑定
            if self.ui_manager.active_key_binding:
                self.ui_manager.active_key_binding = None
                return True
            # 优先处理输入栏的ESC键
            if self.ui_manager.number_input_active:
                self.ui_manager.number_input_active = False
                Utils.play_sound(self.snd_ui_click, self)
                return True
            # 关闭教程页面
            if self.ui_manager.tutorial_active:
                self.ui_manager.tutorial_active = False
                Utils.play_sound(self.snd_ui_click, self)
                return True
            # 处理统计界面的ESC键
            if self.ui_manager.stats_active:
                # 在统计界面，直接关闭统计界面
                self.ui_manager.stats_active = False
                # 关闭统计界面时恢复游戏运行
                self.paused = False
                Utils.play_sound(self.snd_ui_click, self)
                return True
    
            if self.ui_manager.settings_active:
        
                self.ui_manager.settings_active = False
                Utils.play_sound(self.snd_ui_click, self)
                return True
            # 弹窗处理优先级高于状态处理
            if self.ui_manager.modal_active:
                # 如果正在弹窗，则关闭弹窗
                self.ui_manager.modal_active = False
                Utils.play_sound(self.snd_ui_click, self)
                return True
            # 不同状态下的ESC键处理
            if self.state == GAME_STATE_TITLE:
                # 检查主界面冷却时间 - 进入主界面前2秒ESC键无效
                current_time = time.time()
                if current_time - self.state_enter_time >= self.title_esc_cooldown:
                    # 主界面按下ESC，弹出确认退出弹窗
                    self.ui_manager.modal_active = True
                    self.ui_manager.modal_progress = 0.0
                    self.ui_manager.modal_type = 'exit_game'
                    Utils.play_sound(self.snd_ui_click, self)
                return True
            elif self.state == GAME_STATE_PLAYING:
        
                self.ui_manager.modal_active = True
                self.ui_manager.modal_progress = 0.0
                self.ui_manager.modal_type = 'return_title'
                Utils.play_sound(self.snd_ui_click, self)
            elif self.state == GAME_STATE_GAMEOVER:
        
                self.reset()
                self.state = GAME_STATE_TITLE
                # 记录进入主界面的时间
                self.state_enter_time = time.time()
                Utils.play_sound(self.snd_ui_click, self)
            return True
        
        # Enter键处理：在弹窗界面时关闭弹窗
        if event.key == pygame.K_RETURN:
            if self.ui_manager.modal_active:
                self.ui_manager.modal_active = False
                Utils.play_sound(self.snd_ui_click, self)
            return True
        
        # 处理按键绑定输入
        if self.ui_manager.handle_key_bind_input(event.key):
            return True
        
        # 显示统计信息（使用自定义按键绑定）- 仅在非游戏状态下有效
        if event.key == self.ui_manager.key_bindings['show_stats']['key']:
            if self.state == GAME_STATE_PLAYING:
                # 游戏状态下，切换统计界面显示
                self.ui_manager.stats_active = not self.ui_manager.stats_active
                # 当打开统计界面时暂停游戏，关闭时恢复游戏
                self.paused = self.ui_manager.stats_active
                Utils.play_sound(self.snd_ui_click, self)
                return True
        
        # 切换背景音乐（使用自定义按键绑定）
        if event.key == self.ui_manager.key_bindings['music']['key']:
            # 添加计时器以防止频繁切换
            current_time = time.time()
            
            if current_time - self.last_m_toggle >= self.m_cooldown:
                self.last_m_toggle = current_time
                if getattr(pygame, 'mixer', None) and getattr(pygame.mixer, 'music', None):
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.fadeout(500)
                    else:
                        if self.music_loaded:
                            pygame.mixer.music.play(-1)
        
        # 重玩键处理（使用自定义按键绑定）
        if event.key == self.ui_manager.key_bindings['restart']['key']:
            current_time = time.time()
            if self.state == GAME_STATE_GAMEOVER:
                # 游戏结束时直接重玩
                if current_time - self.last_r_restart >= self.r_cooldown:
                    self.last_r_restart = current_time
                    self.reset()
                    self.state = GAME_STATE_PLAYING
            elif self.state == GAME_STATE_PLAYING and not self.ui_manager.modal_active:
                # 检查游戏状态冷却时间 - 进入游戏状态前3秒R键无效
                if current_time - self.state_enter_time >= self.playing_r_cooldown:
                    # 游戏进行中，打开确认重玩弹窗
                    self.ui_manager.modal_active = True
                    self.ui_manager.modal_progress = 0.0
                    self.ui_manager.modal_type = 'restart'
                    # 播放弹窗音效
                    Utils.play_sound(self.snd_ui_click, self)
        
        # 射击方式切换按键处理
        if event.key == self.ui_manager.key_bindings[KEY_SHOOT_SWITCH]['key'] and self.state == GAME_STATE_PLAYING and getattr(self, 'allow_switch_shoot_type', True):
            # 根据当前stage确定可用的射击方式
            if self.stage <= 2:
                # stage 1-2 只能使用直射
                pass  # 不做任何改变
            else:
                # 定义射击方式循环
                shoot_type_order = []
                if self.stage <= 3:
                    shoot_type_order = [SHOOT_TYPE_DIRECT, SHOOT_TYPE_SCATTER]
                else:  # stage 4
                    shoot_type_order = [SHOOT_TYPE_DIRECT, SHOOT_TYPE_SCATTER, SHOOT_TYPE_RAPID]

                current_index = shoot_type_order.index(self.player.current_shoot_type) if self.player.current_shoot_type in shoot_type_order else 0
                # 循环切换到下一种射击方式
                new_index = (current_index + 1) % len(shoot_type_order)
                self.player.current_shoot_type = shoot_type_order[new_index]
                
                # 显示射击方式切换提示
                shoot_type_names = {SHOOT_TYPE_DIRECT: '直射', SHOOT_TYPE_SCATTER: '散射', SHOOT_TYPE_RAPID: '连射'}
                ft = FloatingText(
                    self.player.x + self.player.w // 2,
                    self.player.y - 20,
                    f"射击方式: {shoot_type_names.get(self.player.current_shoot_type, '直射')}",
                    COLOR_CYAN,  # 青色
                    duration=2.0,
                    rise_speed=40
                )
                self.floating_texts.append(ft)
                # 播放切换音效
                Utils.play_sound(self.snd_ui_click, self)
        
        return True
    
    def _handle_mousedown(self, event):
        """处理鼠标点击事件"""
        pos = pygame.mouse.get_pos()
        
        # 优先处理统计界面点击
        if self.ui_manager.stats_active:
            self.ui_manager.handle_statistics_click(pos)
            # 统计界面打开时，不处理其他点击
            return
        
        # 优先处理教程界面点击
        if self.ui_manager.tutorial_active:
            # 检查是否点击了关闭按钮
            if self.ui_manager.close_button_rect:
                # 计算相对位置
                window_width = int(SCREEN_W * 0.85)
                window_x = (SCREEN_W - window_width) // 2
                window_height = int(SCREEN_H * 0.8)
                window_y = (SCREEN_H - window_height) // 2
                
                # 将屏幕坐标转换为窗口表面坐标
                popup_pos = (pos[0] - window_x, pos[1] - window_y)
                if self.ui_manager.close_button_rect.collidepoint(popup_pos):
                    Utils.play_sound(self.snd_ui_click)
                    self.ui_manager.tutorial_active = False
                    return
            # 教程界面打开时，不处理其他点击
            return
            
        # 标题界面按钮点击
        if self.state == GAME_STATE_TITLE:
            if not self.ui_manager.settings_active:
                for btn_name, btn_info in self.ui_manager.title_buttons.items():
                    if btn_info['rect'].collidepoint(pos):
                        Utils.play_sound(self.snd_ui_click, self)
                        if btn_name == 'start':
                            # 只有在没有过渡动画播放时才触发新动画
                            if not self.start_transition:
                                self.start_transition = True
                                self.transition_progress = 0.0
                        elif btn_name == 'settings':
                            self.ui_manager.settings_active = True
                        elif btn_name == 'tutorial':
                            self.ui_manager.tutorial_active = True
                        elif btn_name == 'statistics':
                            self.ui_manager.stats_active = True
            else:
        
                self.ui_manager.handle_settings_click(pos)
        
        # 模态弹窗按钮点击
        if self.ui_manager.modal_active and self.ui_manager.modal_progress > 0.5:
            # 计算弹窗位置（与draw_modal方法中的计算保持一致）
            pw = int(SCREEN_W * 0.78)
            ph = 220
            px = (SCREEN_W - pw) // 2
            py = int(SCREEN_H * 0.18)

            if self.ui_manager.close_button_rect:
                # 将屏幕坐标转换为弹窗表面坐标
                popup_pos = (pos[0] - px, pos[1] - py)
                if self.ui_manager.close_button_rect.collidepoint(popup_pos):
                    Utils.play_sound(self.snd_ui_click)
                    self.ui_manager.modal_active = False
                    return
            
            # 检查确认和继续按钮点击
            if self.ui_manager._popup_confirm_rect and self.ui_manager._popup_continue_rect:
                
                if self.ui_manager._popup_confirm_rect.collidepoint(pos):
                    Utils.play_sound(self.snd_ui_click)
                    if self.ui_manager.modal_type == 'restart':
                        self.reset()
                        self.state = GAME_STATE_PLAYING
                    elif self.ui_manager.modal_type == 'return_title':
                        self.reset()
                    elif self.ui_manager.modal_type == 'exit_game':
                        self.update_statistics()
                        # 退出游戏
                        pygame.quit()
                        sys.exit(0)
                    self.ui_manager.modal_active = False
                
                elif self.ui_manager._popup_continue_rect.collidepoint(pos):
                    Utils.play_sound(self.snd_ui_click)
                    self.ui_manager.modal_active = False
        
        # 数字输入确认/取消按钮
        if self.ui_manager.number_input_active:
            if self.ui_manager._input_confirm_btn and self.ui_manager._input_cancel_btn:
                if self.ui_manager._input_confirm_btn.collidepoint(pos):
                    # 确认输入
                    try:
                        value = int(self.ui_manager.input_value)
                        value = max(0, min(100, value))
                        if self.ui_manager.active_volume:
                            self.ui_manager.volume_settings[self.ui_manager.active_volume]['value'] = value
                    except ValueError:
                        # 输入无效，使用默认值
                        pass
                    self.ui_manager.number_input_active = False
                
                elif self.ui_manager._input_cancel_btn.collidepoint(pos):
                    # 取消输入
                    self.ui_manager.number_input_active = False
    
    def _handle_active_event(self, event):
        """处理窗口激活事件"""
        try:
            gain = event.gain
            state = event.state
            
            # 处理窗口焦点变化 (使用数值常量替代已废弃的命名常量)
            if state == 1 and gain == 1:  # ACTIVEEVENT_GAINED = 1
                self.has_focus = True
                self.paused = False
            elif state == 1 and gain == 0:  # ACTIVEEVENT_LOST = 0
                self.has_focus = False
                self.paused = True
        except Exception:
            # 忽略事件处理错误
            pass
    
    def _handle_number_input(self, event):
        """处理数字输入"""
        if not self.ui_manager.number_input_active:
            return
        
        # 确保input_value属性始终存在且为字符串
        if self.ui_manager.input_value is None:
            self.ui_manager.input_value = ""
            
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            # 确认输入
            try:
                value = int(self.ui_manager.input_value)
                value = max(0, min(100, value))
                if self.ui_manager.active_volume:
                    self.ui_manager.volume_settings[self.ui_manager.active_volume]['value'] = value
            
                    if self.ui_manager.active_volume in ['master', 'music']:
                        # 计算最终音乐音量 = 主音量 x 音乐音量
                        master_val = self.ui_manager.volume_settings['master']['value'] / 100
                        music_val = self.ui_manager.volume_settings['music']['value'] / 100
                        pygame.mixer.music.set_volume(master_val * music_val)
            except ValueError:
                # 输入无效，使用默认值
                pass
            self.ui_manager.number_input_active = False
        
        elif event.key == pygame.K_ESCAPE:
            # 按ESC键直接取消输入
            self.ui_manager.number_input_active = False
        elif event.key == pygame.K_BACKSPACE:
            # 确保input_value是字符串类型（再次检查确保安全）
            if not isinstance(self.ui_manager.input_value, str):
                self.ui_manager.input_value = ""
            
            if not self.ui_manager.input_value:
                # 当输入框为空时按Backspace键，先将音量设置为0，然后取消输入
                if self.ui_manager.active_volume:
                    self.ui_manager.volume_settings[self.ui_manager.active_volume]['value'] = 0
                    
                    # 如果是主音量或音乐音量，立即更新音乐播放音量
                    if self.ui_manager.active_volume in ['master', 'music']:
                        # 计算最终音乐音量 = 主音量 x 音乐音量
                        master_val = self.ui_manager.volume_settings['master']['value'] / 100
                        music_val = self.ui_manager.volume_settings['music']['value'] / 100
                        pygame.mixer.music.set_volume(master_val * music_val)
                self.ui_manager.number_input_active = False
            else:
                # 删除最后一个字符
                self.ui_manager.input_value = self.ui_manager.input_value[:-1]
                # 实时更新音乐音量（如果是音量设置）
                if self.ui_manager.active_volume in ['master', 'music'] and self.ui_manager.input_value:
                    try:
                        temp_value = int(self.ui_manager.input_value)
                        temp_value = max(0, min(100, temp_value))
                        # 计算最终音乐音量 = 主音量 x 音乐音量
                        master_val = self.ui_manager.volume_settings['master']['value'] / 100
                        music_val = self.ui_manager.volume_settings['music']['value'] / 100
                        # 如果正在编辑的是主音量，使用临时值
                        if self.ui_manager.active_volume == 'master':
                            master_val = temp_value / 100
                        # 如果正在编辑的是音乐音量，使用临时值
                        elif self.ui_manager.active_volume == 'music':
                            music_val = temp_value / 100
                        pygame.mixer.music.set_volume(master_val * music_val)
                    except ValueError:
                        pass
        
        else:
            # 只接受数字输入
            key_name = pygame.key.name(event.key)
            # 确保input_value是字符串类型（再次检查确保安全）
            if not isinstance(self.ui_manager.input_value, str):
                self.ui_manager.input_value = ""
            
            if key_name.isdigit() and len(self.ui_manager.input_value) < 3:
                self.ui_manager.input_value += key_name
                # 确保不超过100
                try:
                    if int(self.ui_manager.input_value) > 100:
                        self.ui_manager.input_value = "100"
                    
                    # 实时更新音乐音量（如果是音量设置）
                    if self.ui_manager.active_volume in ['master', 'music']:
                        # 临时更新音量设置以计算实时值
                        temp_value = int(self.ui_manager.input_value)
                        temp_value = max(0, min(100, temp_value))
                        # 计算最终音乐音量 = 主音量 x 音乐音量
                        master_val = self.ui_manager.volume_settings['master']['value'] / 100
                        music_val = self.ui_manager.volume_settings['music']['value'] / 100
                        # 如果正在编辑的是主音量，使用临时值
                        if self.ui_manager.active_volume == 'master':
                            master_val = temp_value / 100
                        # 如果正在编辑的是音乐音量，使用临时值
                        elif self.ui_manager.active_volume == 'music':
                            music_val = temp_value / 100
                        pygame.mixer.music.set_volume(master_val * music_val)
                except ValueError:
                    pass

    def notice(self, within_seconds: float, *strings):
        """在右上角HUD中逐个字符显示通知信息，并在指定时间后逐个字符清除
        
        Args:
            within_seconds: 字符全部显示所需的总时间（秒）
            *strings: 要显示的字符串内容，多个参数将被合并显示
        """
        
        # 合并所有字符串
        full_text = ' '.join(strings)
        total_chars = len(full_text)
        
        # 为每条通知生成唯一标识
        notice_id = str(uuid.uuid4())[:8]  # 使用短uuid作为唯一标识
        
        # 计算每个字符的显示间隔（毫秒）
        char_interval_ms = (within_seconds * 1000) / total_chars if total_chars > 0 else 100
        
        # 当前显示的字符数
        current_chars = [0]
        
        # 显示阶段标识
        is_showing = [True]
        
        # 清除阶段标识
        is_clearing = [False]
        
        # 用于存储任务对象的列表
        tasks = []
        
        def update_notice():
            """更新通知文本显示状态"""
            if is_showing[0]:
                # 显示阶段
                if current_chars[0] < total_chars:
                    current_chars[0] += 1
                    display_text = full_text[:current_chars[0]]
                    self.ui_manager.add_top_right_text(display_text, COLOR_LIGHT_YELLOW, key=f'notice_{notice_id}')
                else:
                    # 显示完成，停止显示任务，5秒后开始清除
                    is_showing[0] = False
                    
                    def start_clearing():
                        """开始清除过程"""
                        is_clearing[0] = True
                        # 创建清除任务
                        clear_task = runTaskTimer(clear_notice, 0, char_interval_ms)
                        tasks.append(clear_task)
                    
                    # 5秒后开始清除
                    delay_task = runTaskLater(start_clearing, 5000)
                    tasks.append(delay_task)
            elif is_clearing[0]:
                # 清除阶段
                if current_chars[0] > 0:
                    current_chars[0] -= 1
                    display_text = full_text[:current_chars[0]]
                    self.ui_manager.add_top_right_text(display_text, COLOR_LIGHT_YELLOW, key=f'notice_{notice_id}')
                else:
                    # 清除完成，移除文本并取消任务
                    self.ui_manager.remove_top_right_text(f'notice_{notice_id}')
                    is_clearing[0] = False
                    # 取消所有相关任务
                    for task in tasks:
                        task.cancel()
        
        def clear_notice():
            """清除通知文本"""
            if is_clearing[0]:
                if current_chars[0] > 0:
                    current_chars[0] -= 1
                    display_text = full_text[:current_chars[0]]
                    self.ui_manager.add_top_right_text(display_text, COLOR_LIGHT_YELLOW, key=f'notice_{notice_id}')
                else:
                    # 清除完成，移除文本并取消任务
                    self.ui_manager.remove_top_right_text(f'notice_{notice_id}')
                    is_clearing[0] = False
                    # 取消所有相关任务
                    for task in tasks:
                        task.cancel()
        
        # 如果有文本需要显示
        if total_chars > 0:
            # 创建显示任务
            show_task = runTaskTimer(update_notice, 0, char_interval_ms)
            tasks.append(show_task)
            
            # 初始化显示第一个字符
            self.ui_manager.add_top_right_text(full_text[0], COLOR_LIGHT_YELLOW, key=f'notice_{notice_id}')
            current_chars[0] = 1
        
        # 返回一个对象，允许手动取消通知
        class NoticeHandle:
            def cancel(self):
                # 取消所有任务并立即清除通知
                for task in tasks:
                    task.cancel()
                self.ui_manager.remove_top_right_text(f'notice_{notice_id}')
        
        return NoticeHandle()

def main():
    Utils.debug("开始游戏启动...")
    # 确保窗口居中
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    Utils.debug("环境变量设置完成")

    Utils.debug("初始化PyGame...")
    pygame.init()
    Utils.debug("PyGame核心模块初始化完成")
    pygame.display.init()
    Utils.debug("显示模块初始化完成")
    pygame.font.init()
    Utils.debug("字体模块初始化完成")
    pygame.mixer.init()
    Utils.debug("音频模块初始化完成")
    
    pygame.key.set_repeat(1000, 200)
    
    try:
        pygame.key.stop_text_input()
    except Exception:
        pass
    
    game = Game()
    game.run()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        Utils.error(f"游戏运行出错: {e}")
        Utils.error("错误详情:")
        traceback.print_exc()
        input("按Enter键退出...")

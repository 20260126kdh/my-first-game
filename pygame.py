"""
⚔️  SPEAR DUNGEON  ⚔️
픽셀 던전풍 사이드뷰 로그라이크 액션 게임

조작:
  WASD         - 이동
  좌클릭        - 찌르기 (마우스 방향, 풍압 이펙트)
  우클릭 홀드   - 창 돌리기 (0.5초 → 패링 판정)
                  패링 성공 후 좌클릭 → 카운터 공격
  E키           - 창 투척 (적에게 박힘)
  ESC          - 종료
"""

import pygame, math, random, sys

# ──────────────────────────────────────────────
#  상수
# ──────────────────────────────────────────────
SCREEN_W, SCREEN_H = 900, 600
FPS       = 60
TILE      = 40
ROOM_COLS = 20
ROOM_ROWS = 13
ROOM_W    = ROOM_COLS * TILE
ROOM_H    = ROOM_ROWS * TILE

# 팔레트
C_BG        = (18,  14,  26)
C_FLOOR     = (52,  40,  60)
C_FLOOR2    = (44,  34,  52)
C_WALL      = (28,  22,  42)
C_WALL_TOP  = (72,  58,  90)
C_PLAYER    = (100, 200, 240)
C_PLAYER_SH = (60,  140, 180)
C_SPEAR     = (240, 220, 100)
C_ENEMY     = (220, 80,  80)
C_ENEMY_SH  = (160, 40,  40)
C_BOSS      = (200, 60,  200)
C_BOSS_SH   = (130, 20,  130)
C_HP_RED    = (220, 50,  50)
C_HP_GREEN  = (80,  200, 100)
C_HP_BACK   = (40,  20,  20)
C_DOOR      = (180, 140, 60)
C_DOOR_OPEN = (240, 200, 100)
C_TIMER_OK  = (80,  220, 120)
C_TIMER_WARN= (240, 180, 40)
C_TIMER_CRIT= (240, 60,  60)
C_GOLD      = (255, 210, 50)
C_WHITE     = (255, 255, 255)
C_DARK      = (0,   0,   0)
C_SHADOW    = (10,  8,   16)
C_PARRY     = (120, 220, 255)
C_COUNTER   = (255, 120, 30)
C_WIND      = (180, 230, 255)

# 게임 수치
TIME_LIMIT       = 60
PLAYER_SPEED     = 4
PLAYER_HP        = 100

# 찌르기
STAB_DMG         = 35
STAB_RANGE       = 90      # px
STAB_COOLDOWN    = 18      # 프레임
STAB_ANIM_FRAMES = 10

# 패링/카운터
PARRY_SPIN_TIME  = 0.5     # 초 (이 시간 동안 돌리면 패링 준비)
PARRY_WINDOW     = 45      # 패링 후 카운터 가능 프레임
COUNTER_DMG      = 80
COUNTER_RANGE    = 110

# 투척
THROW_SPEED      = 13
THROW_RANGE      = 500
THROW_DMG        = 45
THROW_COOLDOWN   = 25

ENEMY_TYPES = [
    {"name":"슬라임", "hp":50,  "speed":1.5,"dmg":8, "size":18,
     "color":C_ENEMY,        "shadow":C_ENEMY_SH,    "score":10},
    {"name":"해골",   "hp":80,  "speed":2.2,"dmg":12,"size":16,
     "color":(180,180,180),  "shadow":(100,100,100), "score":20},
    {"name":"오우거", "hp":140, "speed":1.2,"dmg":20,"size":26,
     "color":(100,180,80),   "shadow":(60,110,40),   "score":40},
]
BOSS_DATA = {"name":"암흑 군주","hp":400,"speed":1.8,"dmg":25,"size":36,
             "color":C_BOSS,"shadow":C_BOSS_SH,"score":200}

# ──────────────────────────────────────────────
#  유틸
# ──────────────────────────────────────────────
def dist(ax,ay,bx,by): return math.hypot(ax-bx, ay-by)

def normalize(dx,dy):
    d = math.hypot(dx,dy)
    return (0,0) if d==0 else (dx/d, dy/d)

def pixel_font(size):
    return pygame.font.SysFont("monospace", size, bold=True)

def draw_text_shadow(surf,text,font,color,x,y,shadow=C_SHADOW):
    surf.blit(font.render(text,False,shadow),(x+2,y+2))
    surf.blit(font.render(text,False,color),(x,y))

def draw_bar(surf,x,y,w,h,val,mx,c_fill,c_back=C_HP_BACK):
    pygame.draw.rect(surf,c_back,(x,y,w,h))
    fill = int(w*max(0,val)/max(1,mx))
    if fill>0: pygame.draw.rect(surf,c_fill,(x,y,fill,h))
    pygame.draw.rect(surf,C_WHITE,(x,y,w,h),1)

# ──────────────────────────────────────────────
#  파티클
# ──────────────────────────────────────────────
class Particle:
    def __init__(self,x,y,color,vx,vy,life=30,size=4):
        self.x,self.y=x,y
        self.color=color; self.vx,self.vy=vx,vy
        self.life=self.max_life=life; self.size=size
    def update(self):
        self.x+=self.vx; self.y+=self.vy
        self.vy+=0.12; self.life-=1
    def draw(self,surf,cx,cy):
        a=self.life/self.max_life
        r=max(1,int(self.size*a))
        bx,by=int(self.x-cx),int(self.y-cy)
        c=tuple(int(v*a) for v in self.color)
        pygame.draw.rect(surf,c,(bx-r//2,by-r//2,r,r))

def spawn_particles(particles,x,y,color,count=10):
    for _ in range(count):
        a=random.uniform(0,math.pi*2)
        s=random.uniform(1,4)
        particles.append(Particle(x,y,color,
            math.cos(a)*s, math.sin(a)*s-1,
            life=random.randint(20,40),
            size=random.randint(3,7)))

# 풍압 이펙트 전용 파티클 (가로로 길게 퍼지는 선)
class WindParticle:
    def __init__(self,x,y,angle):
        self.x,self.y=float(x),float(y)
        spread = random.uniform(-0.35,0.35)
        base_spd = random.uniform(5,10)
        self.vx = math.cos(angle+spread)*base_spd
        self.vy = math.sin(angle+spread)*base_spd
        self.life = self.max_life = random.randint(8,16)
        self.length = random.randint(10,22)
        self.angle = angle+spread
    def update(self):
        self.x+=self.vx; self.y+=self.vy
        self.vx*=0.85;   self.vy*=0.85
        self.life-=1
    def draw(self,surf,cx,cy):
        a=self.life/self.max_life
        alpha_c = tuple(int(v*a) for v in C_WIND)
        bx,by=int(self.x-cx),int(self.y-cy)
        ex=bx+int(math.cos(self.angle)*self.length*a)
        ey=by+int(math.sin(self.angle)*self.length*a)
        if alpha_c[0]>0:
            pygame.draw.line(surf,alpha_c,(bx,by),(ex,ey),2)

# ──────────────────────────────────────────────
#  박힌 창 (ThrownSpear가 적에게 닿으면 생성)
# ──────────────────────────────────────────────
class StuckSpear:
    """적 몸에 박힌 창 — 적과 함께 움직이며 렌더링"""
    def __init__(self, offset_x, offset_y, angle):
        self.ox = offset_x   # 적 cx 기준 오프셋
        self.oy = offset_y
        self.angle = angle

    def draw(self, surf, ex, ey, cam_x, cam_y):
        sx = int(ex - cam_x)
        sy = int(ey - cam_y)
        length = 26
        tip_x = sx + int(math.cos(self.angle)*length)
        tip_y = sy + int(math.sin(self.angle)*length)
        tail_x = sx - int(math.cos(self.angle)*18)
        tail_y = sy - int(math.sin(self.angle)*18)
        pygame.draw.line(surf,(160,120,60),(tail_x,tail_y),(sx,sy),3)
        pygame.draw.line(surf,C_SPEAR,(sx,sy),(tip_x,tip_y),3)

# ──────────────────────────────────────────────
#  투척 창
# ──────────────────────────────────────────────
class ThrownSpear:
    def __init__(self,x,y,angle):
        self.x,self.y=float(x),float(y)
        self.angle=angle
        self.vx=math.cos(angle)*THROW_SPEED
        self.vy=math.sin(angle)*THROW_SPEED
        self.traveled=0
        self.alive=True
        self.stuck_to=None   # 박힌 적 객체
    @property
    def cx(self): return self.x
    @property
    def cy(self): return self.y

    def update(self, walls, enemies, particles, player):
        if self.stuck_to is not None:
            # 적이 죽으면 창도 소멸
            if not self.stuck_to.alive:
                self.alive = False
            return
        self.x+=self.vx; self.y+=self.vy
        self.traveled+=THROW_SPEED
        if self.traveled>THROW_RANGE:
            self.alive=False; return
        r=pygame.Rect(int(self.x)-4,int(self.y)-4,8,8)
        for w in walls:
            if r.colliderect(w):
                self.alive=False; return
        for e in enemies:
            if e.alive and dist(self.x,self.y,e.cx,e.cy)<e.size+6:
                e.take_damage(THROW_DMG)
                spawn_particles(particles,e.cx,e.cy,e.color,14)
                player.score += e.score//3
                if not e.alive:
                    player.score += e.score
                # 적이 살아있으면 박힘
                if e.alive:
                    ox = self.x - e.cx
                    oy = self.y - e.cy
                    e.stuck_spears.append(StuckSpear(ox,oy,self.angle))
                    self.alive = False
                else:
                    self.alive = False
                return

    def draw(self,surf,cam_x,cam_y):
        if self.stuck_to: return
        sx=int(self.x-cam_x); sy=int(self.y-cam_y)
        length=26
        tail_x=sx-int(math.cos(self.angle)*18)
        tail_y=sy-int(math.sin(self.angle)*18)
        tip_x =sx+int(math.cos(self.angle)*length)
        tip_y =sy+int(math.sin(self.angle)*length)
        pygame.draw.line(surf,(160,120,60),(tail_x,tail_y),(sx,sy),3)
        pygame.draw.line(surf,C_SPEAR,(sx,sy),(tip_x,tip_y),3)

# ──────────────────────────────────────────────
#  플레이어
# ──────────────────────────────────────────────
# 공격 상태 머신
ATTACK_NONE    = 0
ATTACK_STAB    = 1   # 찌르기 진행 중
ATTACK_SPIN    = 2   # 창 돌리기 (우클릭 홀드)
ATTACK_PARRIED = 3   # 패링 성공 — 카운터 대기
ATTACK_COUNTER = 4   # 카운터 공격 진행 중

class Player:
    def __init__(self,x,y):
        self.x,self.y=float(x),float(y)
        self.w,self.h=24,32
        self.hp=PLAYER_HP; self.max_hp=PLAYER_HP
        self.facing=1
        self.invincible=0
        self.score=0
        self.bob=0

        # ── 공격 상태 ──
        self.attack_state = ATTACK_NONE
        self.stab_frame   = 0      # 찌르기 애니메이션
        self.stab_angle   = 0
        self.spin_time    = 0.0    # 우클릭 홀드 누적 시간(초)
        self.parry_frames = 0      # 패링 후 카운터 가능 시간
        self.counter_frame= 0
        self.counter_angle= 0
        self.throw_cooldown=0
        self.stab_cooldown =0

        # 창 각도 (보유 중일 때 마우스 방향)
        self.spear_angle  = 0.0

        # 박힌 창이 없으면 1개 보유
        self.has_spear    = True

        # 강화 카운터 (SPIN 중 피격 시 활성화)
        self.counter_enhanced = False   # True이면 빨간 강화 카운터

        # 강화 카운터 돌진
        self.dash_vx      = 0.0   # 돌진 속도 벡터
        self.dash_vy      = 0.0
        self.dash_frames  = 0     # 남은 돌진 프레임
        self.dash_trail   = []    # 잔상 위치 리스트 [(x,y), ...]
        self.dash_hit_targets=set()

    @property
    def cx(self): return self.x+self.w/2
    @property
    def cy(self): return self.y+self.h/2
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.w,self.h)

    # ── 매 프레임 갱신 ──
    def update(self, keys, dt, walls, mx, my, cam_x, cam_y,
               enemies, particles, thrown_spears,
               mb_left, mb_right, key_e_pressed, key_r_pressed=False):

        # 마우스 방향 → 창 각도
        wx=mx+cam_x; wy=my+cam_y
        self.spear_angle = math.atan2(wy-self.cy, wx-self.cx)
        if wx > self.cx: self.facing=1
        elif wx < self.cx: self.facing=-1

        # 이동
        dx,dy=0,0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx-=PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx+=PLAYER_SPEED
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy-=PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy+=PLAYER_SPEED
        if dx and dy: dx*=0.707; dy*=0.707
        if dx: self._move_axis(dx,0,walls)
        if dy: self._move_axis(0,dy,walls)
        if dx or dy: self.bob=(self.bob+1)%12
        else: self.bob=0

        # 쿨다운
        if self.stab_cooldown>0:  self.stab_cooldown-=1
        if self.throw_cooldown>0: self.throw_cooldown-=1
        if self.invincible>0:     self.invincible-=1

        # ── 공격 상태 머신 ──
        if key_r_pressed and not self.has_spear:
            self.has_spear=True

        if self.dash_frames>0:
            self.x += self.dash_vx
            self.y += self.dash_vy
            self.dash_frames -= 1
            self.dash_trail.append((self.x,self.y))
            self.dash_trail=self.dash_trail[-8:]

        self._update_attack(dt, mb_left, mb_right, key_e_pressed,
                            mx, my, cam_x, cam_y,
                            enemies, particles, thrown_spears)

    def _update_attack(self, dt, mb_left, mb_right, key_e,
                       mx, my, cam_x, cam_y,
                       enemies, particles, thrown_spears):

        state = self.attack_state

        # ────────────────────────────
        # NONE 상태: 입력 감지
        # ────────────────────────────
        if state == ATTACK_NONE:
            # E키: 투척
            if key_e and self.has_spear and self.throw_cooldown==0:
                wx=mx+cam_x; wy=my+cam_y
                angle=math.atan2(wy-self.cy, wx-self.cx)
                thrown_spears.append(ThrownSpear(self.cx,self.cy,angle))
                self.has_spear=False
                self.throw_cooldown=THROW_COOLDOWN

            # 좌클릭: 찌르기
            elif mb_left and self.stab_cooldown==0 and self.has_spear:
                self.attack_state=ATTACK_STAB
                self.stab_frame=STAB_ANIM_FRAMES
                self.stab_angle=self.spear_angle
                self._do_stab(enemies, particles)

            # 우클릭 홀드: 창 돌리기 시작
            elif mb_right:
                self.attack_state=ATTACK_SPIN
                self.spin_time=0.0

        # ────────────────────────────
        # STAB 상태
        # ────────────────────────────
        elif state == ATTACK_STAB:
            self.stab_frame-=1
            if self.stab_frame<=0:
                self.attack_state=ATTACK_NONE
                self.stab_cooldown=STAB_COOLDOWN

        # ────────────────────────────
        # SPIN 상태 (우클릭 홀드)
        # ────────────────────────────
        elif state == ATTACK_SPIN:
            if not mb_right:
                # 홀드 해제: 그냥 취소
                self.attack_state=ATTACK_NONE
                self.spin_time=0.0
                self.counter_enhanced=False
            else:
                self.spin_time+=dt
                if self.spin_time>=PARRY_SPIN_TIME:
                    # 0.5초 돌리기 완료 → 패링 대기
                    self.attack_state=ATTACK_PARRIED
                    self.parry_frames=PARRY_WINDOW
                    parry_c = (255,60,60) if self.counter_enhanced else C_PARRY
                    spawn_particles(particles,self.cx,self.cy,parry_c,20)

        # ────────────────────────────
        # PARRIED 상태 (카운터 대기)
        # ────────────────────────────
        elif state == ATTACK_PARRIED:
            self.parry_frames-=1
            if self.parry_frames<=0:
                self.attack_state=ATTACK_NONE   # 카운터 창 소진
                self.counter_enhanced=False
            # 좌클릭: 카운터
            elif mb_left:
                enhanced=self.counter_enhanced
                self.attack_state=ATTACK_COUNTER
                self.counter_frame=14
                self.counter_angle=self.spear_angle
                self._do_counter(enemies, particles)
                if enhanced:
                    self.dash_frames=12
                    self.dash_vx=math.cos(self.counter_angle)*18
                    self.dash_vy=math.sin(self.counter_angle)*18
                    self.dash_hit_targets=set()
                self.counter_enhanced=False

        # ────────────────────────────
        # COUNTER 상태
        # ────────────────────────────
        elif state == ATTACK_COUNTER:
            if self.dash_frames>0:
                for e in enemies:
                    if e.alive and id(e) not in self.dash_hit_targets and dist(self.cx,self.cy,e.cx,e.cy)<e.size+24:
                        e.take_damage(120)
                        self.dash_hit_targets.add(id(e))
            self.counter_frame-=1
            if self.counter_frame<=0:
                self.attack_state=ATTACK_NONE
                self.stab_cooldown=STAB_COOLDOWN//2

    def _do_stab(self, enemies, particles):
        """찌르기 — 히트 판정 + 풍압 파티클"""
        angle = self.stab_angle
        # 풍압 파티클
        for _ in range(14):
            particles.append(WindParticle(
                self.cx + math.cos(angle)*30,
                self.cy + math.sin(angle)*30,
                angle))
        # 히트 판정
        for e in enemies:
            if not e.alive: continue
            ex=e.cx-self.cx; ey=e.cy-self.cy
            d=math.hypot(ex,ey)
            if d<STAB_RANGE:
                # 창 방향과 적 방향 각도 차이
                ea=math.atan2(ey,ex)
                diff=abs((ea-angle+math.pi)%(2*math.pi)-math.pi)
                if diff<0.6:   # 좁은 찌르기 판정 각도
                    e.take_damage(STAB_DMG)
                    spawn_particles(particles,e.cx,e.cy,e.color,10)

    def _do_counter(self, enemies, particles):
        """카운터 — 넓은 범위 + 강한 데미지 + 이펙트
        counter_enhanced=True이면 빨간 강화 카운터 (데미지/범위 1.8배)"""
        angle = self.counter_angle
        dmg   = int(COUNTER_DMG * (1.8 if self.counter_enhanced else 1.0))
        rng   = int(COUNTER_RANGE * (1.8 if self.counter_enhanced else 1.0))
        c_col = (255, 40, 40) if self.counter_enhanced else C_COUNTER
        spawn_particles(particles,self.cx,self.cy,c_col,28 if self.counter_enhanced else 20)
        wind_count = 30 if self.counter_enhanced else 20
        for _ in range(wind_count):
            particles.append(WindParticle(
                self.cx+math.cos(angle)*40,
                self.cy+math.sin(angle)*40,
                angle))
        for e in enemies:
            if not e.alive: continue
            d=dist(self.cx,self.cy,e.cx,e.cy)
            if d<rng:
                ea=math.atan2(e.cy-self.cy,e.cx-self.cx)
                diff=abs((ea-angle+math.pi)%(2*math.pi)-math.pi)
                arc = 1.1 if self.counter_enhanced else 0.9
                if diff<arc:
                    e.take_damage(dmg)
                    spawn_particles(particles,e.cx,e.cy,c_col,18)

    def take_damage(self, dmg):
        """패링 중(SPIN/PARRIED)이면 데미지 무효 + 패링 성공 처리"""
        if self.invincible>0: return False
        if self.attack_state in (ATTACK_SPIN, ATTACK_PARRIED):
            # 패링 성공
            if self.attack_state==ATTACK_SPIN and self.spin_time>=0.15:
                self.attack_state=ATTACK_PARRIED
                self.parry_frames=PARRY_WINDOW
                self.counter_enhanced=True   # ★ SPIN 중 피격 → 강화 카운터
            return True   # 패링 성공 신호
        self.hp-=dmg
        self.invincible=60
        return False

    def _move_axis(self,dx,dy,walls):
        self.x+=dx; self.y+=dy
        r=self.rect
        for w in walls:
            if r.colliderect(w):
                if dx>0: self.x=w.left-self.w
                if dx<0: self.x=w.right
                if dy>0: self.y=w.top-self.h
                if dy<0: self.y=w.bottom
                r=self.rect

    # ── 렌더링 ──
    def draw(self, surf, cam_x, cam_y, particles):
        sx=int(self.x-cam_x); sy=int(self.y-cam_y)
        bob_y=int(math.sin(self.bob/6*math.pi)*2)
        angle=self.spear_angle
        state=self.attack_state

        # 무적 깜빡
        if self.invincible>0 and (self.invincible//4)%2==0: return

        for i,(tx,ty) in enumerate(self.dash_trail):
            a=(i+1)/max(1,len(self.dash_trail))
            pygame.draw.rect(surf,(int(255*a),40,40),(int(tx-cam_x),int(ty-cam_y),12,12))
        # 다리
        lo=int(math.sin(self.bob/6*math.pi)*4)
        pygame.draw.rect(surf,C_PLAYER_SH,(sx+4,sy+22-bob_y+lo,7,10))
        pygame.draw.rect(surf,C_PLAYER_SH,(sx+13,sy+22-bob_y-lo,7,10))
        # 몸
        pygame.draw.rect(surf,C_PLAYER,(sx+2,sy+8-bob_y,self.w-4,16))
        # 머리
        pygame.draw.rect(surf,(230,190,150),(sx+5,sy-bob_y,14,12))
        eye_x=sx+(13 if self.facing>0 else 7)
        pygame.draw.rect(surf,C_DARK,(eye_x,sy+3-bob_y,3,3))

        # ── 창 그리기 ──
        pivot_x=sx+self.w//2; pivot_y=sy+self.h//2-2

        if state==ATTACK_SPIN:
            # ── 원형 잔상: 플레이어 주변을 둘러싸는 8개 창 ──
            spin_a = self.spin_time / PARRY_SPIN_TIME * math.pi*4 + angle
            orbit_r = 38  # 플레이어 중심에서 잔상까지 거리
            ghost_count = 8
            # 진행도에 따라 잔상 색 결정 (피격 강화 여부)
            base_c = (255,80,80) if self.counter_enhanced else C_SPEAR
            for i in range(ghost_count):
                ga = spin_a + i*(math.pi*2/ghost_count)
                alpha_ratio = 1.0 - i/ghost_count
                ghost_c = tuple(int(v*alpha_ratio*0.85) for v in base_c)
                ox = int(math.cos(ga)*orbit_r*0.55)
                oy = int(math.sin(ga)*orbit_r*0.55)
                self._draw_spear_at(surf, pivot_x+ox, pivot_y+oy, ga, ghost_c, length=42)
            # 중심 창 (가장 밝게)
            self._draw_spear_at(surf, pivot_x, pivot_y, spin_a, base_c, length=46)

            # 강화 중이면 붉은 글로우 링
            if self.counter_enhanced:
                prog = min(self.spin_time/PARRY_SPIN_TIME, 1.0)
                ring_r = int(50*prog)
                if ring_r>2:
                    rsurf=pygame.Surface((ring_r*2+4,ring_r*2+4),pygame.SRCALPHA)
                    pygame.draw.circle(rsurf,(255,60,60,int(140*prog)),(ring_r+2,ring_r+2),ring_r,3)
                    surf.blit(rsurf,(pivot_x-ring_r-2,pivot_y-ring_r-2))

        elif state==ATTACK_PARRIED:
            # 패링 대기: 창이 빛나며 진동
            jitter = math.sin(self.parry_frames*0.8)*4
            par_c = (255,80,80) if self.counter_enhanced else C_PARRY
            self._draw_spear_at(surf,pivot_x+int(jitter),pivot_y,angle,par_c,length=48)
            # 패링 글로우 원
            prog = self.parry_frames/PARRY_WINDOW
            r_glow = int(28*prog)
            if r_glow>0:
                gsurf=pygame.Surface((r_glow*2,r_glow*2),pygame.SRCALPHA)
                pygame.draw.circle(gsurf,(*par_c,int(90*prog)),(r_glow,r_glow),r_glow)
                surf.blit(gsurf,(pivot_x-r_glow,pivot_y-r_glow))

        elif state==ATTACK_STAB:
            # 찌르기: 창이 앞으로 쭉 뻗음
            prog = 1-(self.stab_frame/STAB_ANIM_FRAMES)
            extend = int(36*math.sin(prog*math.pi))
            self._draw_spear_at(surf,
                pivot_x+int(math.cos(self.stab_angle)*extend),
                pivot_y+int(math.sin(self.stab_angle)*extend),
                self.stab_angle, C_SPEAR, length=46)

        elif state==ATTACK_COUNTER:
            # 카운터: 색상·범위 강화 여부 반영
            c_col = (255,40,40) if self.counter_enhanced else C_COUNTER
            c_rng = int(COUNTER_RANGE*(1.8 if self.counter_enhanced else 1.0))
            prog = 1-(self.counter_frame/14)
            extend = int((60 if self.counter_enhanced else 45)*math.sin(prog*math.pi))
            self._draw_spear_at(surf,
                pivot_x+int(math.cos(self.counter_angle)*extend),
                pivot_y+int(math.sin(self.counter_angle)*extend),
                self.counter_angle, c_col,
                length=56 if self.counter_enhanced else 46)
            # 카운터 부채꼴 이펙트
            arc_w = 1.1 if self.counter_enhanced else 0.8
            a_start=self.counter_angle-arc_w; a_end=self.counter_angle+arc_w
            pts=[(pivot_x,pivot_y)]
            for i in range(15):
                a=a_start+(a_end-a_start)*i/14
                r=int(c_rng*prog)
                pts.append((pivot_x+int(math.cos(a)*r),pivot_y+int(math.sin(a)*r)))
            if len(pts)>=3:
                cs=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
                alpha=int(130*math.sin(prog*math.pi))
                pygame.draw.polygon(cs,(*c_col,alpha),pts)
                surf.blit(cs,(0,0))

        else:
            # 기본 자세: 창 마우스 방향
            if self.has_spear:
                self._draw_spear_at(surf,pivot_x,pivot_y,angle,C_SPEAR,length=44)

    def _draw_spear_at(self, surf, px, py, angle, color, length=44):
        tail_x=px-int(math.cos(angle)*24)
        tail_y=py-int(math.sin(angle)*24)
        tip_x =px+int(math.cos(angle)*length)
        tip_y =py+int(math.sin(angle)*length)
        pygame.draw.line(surf,(140,100,50),(tail_x,tail_y),(px,py),3)
        pygame.draw.line(surf,color,(px,py),(tip_x,tip_y),3)
        # 창날 삼각형
        perp=angle+math.pi/2
        p1=(tip_x,tip_y)
        p2=(tip_x-int(math.cos(angle)*10)+int(math.cos(perp)*5),
            tip_y-int(math.sin(angle)*10)+int(math.sin(perp)*5))
        p3=(tip_x-int(math.cos(angle)*10)-int(math.cos(perp)*5),
            tip_y-int(math.sin(angle)*10)-int(math.sin(perp)*5))
        pygame.draw.polygon(surf,color,[p1,p2,p3])

# ──────────────────────────────────────────────
#  적
# ──────────────────────────────────────────────
class Enemy:
    def __init__(self,x,y,data):
        self.x,self.y=float(x),float(y)
        self.size=data["size"]; self.hp=data["hp"]; self.max_hp=data["hp"]
        self.speed=data["speed"]; self.dmg=data["dmg"]
        self.color=data["color"]; self.shadow=data["shadow"]
        self.name=data["name"]; self.score=data["score"]
        self.alive=True; self.stun=0; self.bob=random.randint(0,12)
        self.stuck_spears=[]   # 박힌 창 목록

    @property
    def cx(self): return self.x
    @property
    def cy(self): return self.y
    @property
    def rect(self):
        return pygame.Rect(int(self.x)-self.size,int(self.y)-self.size,self.size*2,self.size*2)

    def update(self,player,walls,particles):
        self.bob=(self.bob+1)%12
        if self.stun>0: self.stun-=1; return
        dx,dy=player.cx-self.cx,player.cy-self.cy
        ndx,ndy=normalize(dx,dy)
        nx=self.x+ndx*self.speed; ny=self.y+ndy*self.speed
        r=pygame.Rect(int(nx)-self.size,int(ny)-self.size,self.size*2,self.size*2)
        if not any(r.colliderect(w) for w in walls):
            self.x,self.y=nx,ny
        # 접촉 데미지
        if dist(self.cx,self.cy,player.cx,player.cy)<self.size+14:
            parried = player.take_damage(self.dmg)
            if parried:
                spawn_particles(particles,self.cx,self.cy,C_PARRY,12)

    def take_damage(self,dmg):
        self.hp-=dmg; self.stun=12
        if self.hp<=0: self.alive=False

    def draw(self,surf,cam_x,cam_y):
        sx=int(self.x-cam_x); sy=int(self.y-cam_y)
        bob_y=int(math.sin(self.bob/6*math.pi)*2)
        s=self.size
        pygame.draw.ellipse(surf,(0,0,0),(sx-s+2,sy+s-4,s*2-4,8))
        pygame.draw.rect(surf,self.shadow,(sx-s+2,sy-s+2-bob_y,s*2,s*2))
        pygame.draw.rect(surf,self.color,(sx-s,sy-s-bob_y,s*2,s*2))
        pygame.draw.rect(surf,(255,50,50),(sx-4,sy-s+4-bob_y,4,4))
        pygame.draw.rect(surf,(255,50,50),(sx+1,sy-s+4-bob_y,4,4))
        draw_bar(surf,sx-s,sy-s-bob_y-10,s*2,5,self.hp,self.max_hp,C_HP_RED)
        # 박힌 창 렌더링
        for sp in self.stuck_spears:
            sp.draw(surf,self.cx,self.cy,cam_x,cam_y)

class Boss(Enemy):
    def __init__(self,x,y):
        super().__init__(x,y,BOSS_DATA)
        self.phase=1; self.shoot_timer=0
    def update(self,player,walls,particles,projectiles=None):
        if self.hp<self.max_hp*0.5 and self.phase==1:
            self.phase=2; self.speed*=1.5
        super().update(player,walls,particles)
        if projectiles is not None:
            self.shoot_timer-=1
            if self.shoot_timer<=0:
                self.shoot_timer=80 if self.phase==1 else 50
                dx,dy=player.cx-self.cx,player.cy-self.cy
                base=math.atan2(dy,dx)
                for off in [-0.3,0,0.3]:
                    projectiles.append(BossProjectile(self.cx,self.cy,base+off))
    def draw(self,surf,cam_x,cam_y):
        sx=int(self.x-cam_x); sy=int(self.y-cam_y)
        s=self.size; bob_y=int(math.sin(self.bob/6*math.pi)*3)
        cloak_c=(80,20,80) if self.phase==1 else (120,20,20)
        pygame.draw.rect(surf,cloak_c,(sx-s-4,sy-s+8-bob_y,s*2+8,s*2))
        pygame.draw.rect(surf,self.shadow,(sx-s+2,sy-s+2-bob_y,s*2,s*2))
        pygame.draw.rect(surf,self.color,(sx-s,sy-s-bob_y,s*2,s*2))
        crown_c=C_GOLD if self.phase==1 else (255,80,80)
        for i in range(5):
            h=8 if i%2==0 else 5
            pygame.draw.rect(surf,crown_c,(sx-s+i*14,sy-s-8-bob_y,10,h))
        eye_c=(200,100,255) if self.phase==1 else (255,50,50)
        pygame.draw.rect(surf,eye_c,(sx-8,sy-s+6-bob_y,6,6))
        pygame.draw.rect(surf,eye_c,(sx+3,sy-s+6-bob_y,6,6))
        draw_bar(surf,sx-s*2,sy-s-bob_y-14,s*4,8,self.hp,self.max_hp,
                 (200,60,200) if self.phase==1 else (255,60,60))
        fnt=pixel_font(13)
        draw_text_shadow(surf,f"BOSS: {self.name}"+(" [2페이즈]" if self.phase==2 else ""),
                         fnt,C_BOSS,sx-s*2,sy-s-bob_y-28)
        for sp in self.stuck_spears:
            sp.draw(surf,self.cx,self.cy,cam_x,cam_y)

class BossProjectile:
    def __init__(self,x,y,angle):
        self.x,self.y=float(x),float(y)
        self.vx=math.cos(angle)*5; self.vy=math.sin(angle)*5
        self.alive=True; self.traveled=0
    def update(self,walls):
        self.x+=self.vx; self.y+=self.vy; self.traveled+=5
        if self.traveled>500: self.alive=False; return
        r=pygame.Rect(int(self.x)-4,int(self.y)-4,8,8)
        if any(r.colliderect(w) for w in walls): self.alive=False
    def draw(self,surf,cam_x,cam_y):
        sx,sy=int(self.x-cam_x),int(self.y-cam_y)
        pygame.draw.rect(surf,(180,80,255),(sx-5,sy-5,10,10))
        pygame.draw.rect(surf,(220,150,255),(sx-3,sy-3,6,6))

# ──────────────────────────────────────────────
#  방 생성
# ──────────────────────────────────────────────
def build_room(wave):
    walls=[]; obstacles=[]
    for c in range(ROOM_COLS):
        walls.append(pygame.Rect(c*TILE,0,TILE,TILE))
        walls.append(pygame.Rect(c*TILE,(ROOM_ROWS-1)*TILE,TILE,TILE))
    for r in range(1,ROOM_ROWS-1):
        walls.append(pygame.Rect(0,r*TILE,TILE,TILE))
        walls.append(pygame.Rect((ROOM_COLS-1)*TILE,r*TILE,TILE,TILE))
    random.seed(wave*137+42)
    attempts=0
    while len(obstacles)<4+wave and attempts<200:
        attempts+=1
        c=random.randint(3,ROOM_COLS-4); r=random.randint(2,ROOM_ROWS-3)
        rect=pygame.Rect(c*TILE,r*TILE,TILE*random.randint(1,3),TILE)
        safe=[pygame.Rect(TILE,TILE,TILE*3,TILE*3),
              pygame.Rect((ROOM_COLS-3)*TILE,(ROOM_ROWS//2-1)*TILE,TILE*2,TILE*2)]
        if not any(rect.colliderect(s) for s in safe):
            obstacles.append(rect)
    walls.extend(obstacles)
    return walls, obstacles

def spawn_enemies(wave,is_boss_wave,walls):
    enemies=[]; safe=pygame.Rect(TILE,TILE,TILE*4,TILE*4)
    if is_boss_wave:
        enemies.append(Boss(ROOM_W-TILE*4,ROOM_H//2)); return enemies
    count=3+wave*2
    for _ in range(count):
        for _ in range(50):
            x=random.randint(TILE*2,ROOM_W-TILE*2)
            y=random.randint(TILE*2,ROOM_H-TILE*2)
            r=pygame.Rect(x-20,y-20,40,40)
            if not any(r.colliderect(w) for w in walls) and not safe.colliderect(r):
                data=random.choice(ENEMY_TYPES)
                if wave>=2 and random.random()<0.3:
                    data=ENEMY_TYPES[min(wave-1,2)]
                enemies.append(Enemy(float(x),float(y),data)); break
    return enemies

def get_camera(player):
    cx=player.cx-SCREEN_W/2; cy=player.cy-SCREEN_H/2
    return (max(0,min(cx,ROOM_W-SCREEN_W)),
            max(0,min(cy,ROOM_H-SCREEN_H)))

def draw_room(surf,walls,obstacles,cam_x,cam_y,door_open):
    for row in range(1,ROOM_ROWS-1):
        for col in range(1,ROOM_COLS-1):
            c=C_FLOOR if (row+col)%2==0 else C_FLOOR2
            pygame.draw.rect(surf,c,(col*TILE-cam_x,row*TILE-cam_y,TILE,TILE))
    for w in walls:
        if w not in obstacles:
            bx=w.x-cam_x; by=w.y-cam_y
            pygame.draw.rect(surf,C_WALL,(bx,by,TILE,TILE))
            pygame.draw.rect(surf,C_WALL_TOP,(bx,by,TILE,4))
    for o in obstacles:
        bx=o.x-cam_x; by=o.y-cam_y
        pygame.draw.rect(surf,(38,28,55),(bx,by,o.w,o.h))
        pygame.draw.rect(surf,(65,50,80),(bx,by,o.w,4))
        pygame.draw.rect(surf,(65,50,80),(bx,by,4,o.h))
    dx=(ROOM_COLS-1)*TILE-cam_x; dy=(ROOM_ROWS//2-1)*TILE-cam_y
    dc=C_DOOR_OPEN if door_open else C_DOOR
    pygame.draw.rect(surf,dc,(dx,dy,TILE,TILE*2))
    if door_open:
        pygame.draw.rect(surf,C_WHITE,(dx+4,dy+4,TILE-8,TILE*2-8),2)

# ──────────────────────────────────────────────
#  HUD
# ──────────────────────────────────────────────
def draw_hud(surf, player, time_left, wave, is_boss_wave, enemies_left):
    fnt_big  =pixel_font(20); fnt_med=pixel_font(16); fnt_sm=pixel_font(13)

    # HP
    draw_text_shadow(surf,"HP",fnt_sm,C_WHITE,12,10)
    draw_bar(surf,38,12,150,14,player.hp,player.max_hp,C_HP_GREEN)

    # 창 보유
    spear_txt = "[E]창 보유" if player.has_spear else "[E]없음"
    spear_c   = C_SPEAR if player.has_spear else (120,100,80)
    draw_text_shadow(surf,spear_txt,fnt_sm,spear_c,12,32)

    # 공격 상태 표시
    state=player.attack_state
    if state==ATTACK_SPIN:
        prog=min(player.spin_time/PARRY_SPIN_TIME,1.0)
        bar_w=120
        draw_bar(surf,12,52,bar_w,10,prog*100,100,(100,200,255))
        draw_text_shadow(surf,"창 돌리는 중...",fnt_sm,(180,230,255),12,64)
    elif state==ATTACK_PARRIED:
        prog=player.parry_frames/PARRY_WINDOW
        if player.counter_enhanced:
            draw_text_shadow(surf,">> 강화 패링! 카운터 <<",fnt_med,(255,60,60),12,52)
        else:
            draw_text_shadow(surf,">> 패링 성공! 좌클릭으로 카운터 <<",fnt_med,C_PARRY,12,52)
        bar_c=(255,60,60) if player.counter_enhanced else C_PARRY
        draw_bar(surf,12,72,160,8,prog*100,100,bar_c)
    elif state==ATTACK_COUNTER:
        draw_text_shadow(surf,"COUNTER!!",fnt_big,C_COUNTER,12,52)

    # 타이머
    tc=C_TIMER_OK if time_left>20 else (C_TIMER_WARN if time_left>10 else C_TIMER_CRIT)
    draw_text_shadow(surf,f"{int(time_left):02d}s",fnt_big,tc,SCREEN_W//2-22,8)

    # 웨이브
    draw_text_shadow(surf,f"WAVE {wave}"+(" BOSS" if is_boss_wave else ""),
                     fnt_med,C_GOLD,SCREEN_W-160,8)
    draw_text_shadow(surf,f"적 {enemies_left}",fnt_sm,C_WHITE,SCREEN_W-100,30)
    draw_text_shadow(surf,f"SCORE {player.score}",fnt_sm,C_WHITE,SCREEN_W-160,50)

    # 조작 안내
    guide="좌클릭:찌르기  우클릭홀드:패링  E:투척"
    surf.blit(fnt_sm.render(guide,False,(120,100,140)),(10,SCREEN_H-22))

def draw_overlay(surf,title,subtitle,color):
    ov=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
    ov.fill((0,0,0,160)); surf.blit(ov,(0,0))
    ft=pixel_font(52); fs=pixel_font(22)
    t=ft.render(title,False,color)
    s=fs.render(subtitle,False,C_WHITE)
    surf.blit(t,(SCREEN_W//2-t.get_width()//2,SCREEN_H//2-70))
    surf.blit(s,(SCREEN_W//2-s.get_width()//2,SCREEN_H//2+10))

def draw_title(surf,tick):
    surf.fill(C_BG)
    ft=pixel_font(52); fm=pixel_font(22); fs=pixel_font(16)
    pulse=abs(math.sin(tick/40))*30
    c=(int(180+pulse),int(100+pulse//2),int(220+pulse//3))
    t=ft.render("SPEAR DUNGEON",False,c)
    surf.blit(t,(SCREEN_W//2-t.get_width()//2,130))
    s=fm.render("창술로 던전을 탈출하라",False,C_GOLD)
    surf.blit(s,(SCREEN_W//2-s.get_width()//2,210))
    lines=["WASD : 이동",
       "좌클릭 : 찌르기 (풍압 발생)",
       "우클릭 홀드 0.5초 : 패링 준비",
       "  └ 패링 중 피격 → 카운터 대기",
       "  └ 카운터 대기 중 좌클릭 → 카운터!",
       "E : 창 투척 (적에게 박힘)",
       "R : 창 회수"]
    for i,l in enumerate(lines):
        txt=fs.render(l,False,(180,160,200))
        surf.blit(txt,(SCREEN_W//2-txt.get_width()//2,290+i*26))
    blink=fm.render("[ SPACE / ENTER - 시작 ]",False,
                    C_WHITE if (tick//30)%2==0 else (100,80,120))
    surf.blit(blink,(SCREEN_W//2-blink.get_width()//2,460))

# ──────────────────────────────────────────────
#  메인 루프
# ──────────────────────────────────────────────
def game_loop():
    pygame.init()
    pygame.display.set_caption("SPEAR DUNGEON")
    screen=pygame.display.set_mode((SCREEN_W,SCREEN_H))
    clock=pygame.time.Clock()

    S_TITLE="title"; S_PLAY="play"; S_WIN="win"; S_LOSE="lose"
    state=S_TITLE; tick=0

    def init_game():
        pl=Player(TILE*2+8, TILE*3)
        wave=1; is_boss=False
        walls,obstacles=build_room(wave)
        enemies=spawn_enemies(wave,is_boss,walls)
        thrown=[]; projectiles=[]; particles=[]
        tl=float(TIME_LIMIT)
        return pl,wave,is_boss,walls,obstacles,enemies,thrown,projectiles,particles,tl

    pl,wave,is_boss,walls,obstacles,enemies,thrown,projectiles,particles,time_left=init_game()
    door_open=False; final_score=0

    # 마우스 버튼 상태 (이벤트 기반 one-shot + 홀드 구분)
    mb_left_pressed=False    # 이번 프레임 눌렸는지 (one-shot)
    mb_right_held=False      # 현재 홀드 중
    key_e_pressed=False
    key_r_pressed=False

    while True:
        dt=clock.tick(FPS)/1000.0
        tick+=1
        keys=pygame.key.get_pressed()
        mx,my=pygame.mouse.get_pos()

        mb_left_pressed=False
        key_e_pressed=False

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if state==S_TITLE and event.key in (pygame.K_SPACE,pygame.K_RETURN):
                    pl,wave,is_boss,walls,obstacles,enemies,thrown,projectiles,particles,time_left=init_game()
                    door_open=False; state=S_PLAY
                elif state in (S_WIN,S_LOSE):
                    if event.key==pygame.K_r:
                        pl,wave,is_boss,walls,obstacles,enemies,thrown,projectiles,particles,time_left=init_game()
                        door_open=False; state=S_PLAY
                    elif event.key in (pygame.K_SPACE,pygame.K_RETURN):
                        state=S_TITLE
                elif state==S_PLAY and event.key==pygame.K_e:
                    key_e_pressed=True
                elif state==S_PLAY and event.key==pygame.K_r:
                    key_r_pressed=True
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==1: mb_left_pressed=True
                if event.button==3: mb_right_held=True
            if event.type==pygame.MOUSEBUTTONUP:
                if event.button==3: mb_right_held=False

        # ── 타이틀 ──
        if state==S_TITLE:
            draw_title(screen,tick); pygame.display.flip(); continue

        # ── 결과 화면 ──
        if state in (S_WIN,S_LOSE):
            screen.fill(C_BG)
            if state==S_WIN:
                draw_overlay(screen,"CLEAR!",f"점수: {final_score}  |  R:재시작  ENTER:타이틀",C_HP_GREEN)
            else:
                draw_overlay(screen,"GAME OVER",f"점수: {final_score}  |  R:재시작  ENTER:타이틀",C_HP_RED)
            pygame.display.flip(); continue

        # ── 플레이 업데이트 ──
        cam_x,cam_y=get_camera(pl)
        time_left-=dt
        if time_left<=0:
            final_score=pl.score; state=S_LOSE

        pl.update(keys,dt,walls,mx,my,cam_x,cam_y,
                  enemies,particles,thrown,
                  mb_left_pressed,mb_right_held,key_e_pressed,key_r_pressed)

        # 투척 창 업데이트
        for sp in thrown[:]:
            sp.update(walls,enemies,particles,pl)
            if not sp.alive: thrown.remove(sp)

        # 적 업데이트
        for e in enemies[:]:
            if not e.alive:
                spawn_particles(particles,e.cx,e.cy,e.color,20)
                enemies.remove(e); continue
            if isinstance(e,Boss):
                e.update(pl,walls,particles,projectiles)
            else:
                e.update(pl,walls,particles)

        # 보스 투사체
        for p in projectiles[:]:
            p.update(walls)
            if not p.alive: projectiles.remove(p); continue
            if dist(p.x,p.y,pl.cx,pl.cy)<16:
                parried=pl.take_damage(15)
                if parried:
                    spawn_particles(particles,p.x,p.y,C_PARRY,10)
                else:
                    spawn_particles(particles,p.x,p.y,(180,80,255),8)
                projectiles.remove(p)

        # 파티클
        for pt in particles[:]:
            pt.update()
            if pt.life<=0: particles.remove(pt)

        # HP 체크
        if pl.hp<=0:
            final_score=pl.score; state=S_LOSE

        # 문
        door_open=len(enemies)==0
        if door_open:
            door_rect=pygame.Rect((ROOM_COLS-1)*TILE,(ROOM_ROWS//2-1)*TILE,TILE,TILE*2)
            if pl.rect.colliderect(door_rect):
                wave+=1; is_boss=(wave%3==0)
                walls,obstacles=build_room(wave)
                enemies=spawn_enemies(wave,is_boss,walls)
                thrown.clear(); projectiles.clear()
                time_left=TIME_LIMIT+wave*5
                pl.x,pl.y=float(TILE*2+8),float(TILE*3)
                pl.has_spear=True
                pl.hp=min(pl.hp+20,pl.max_hp)
                door_open=False
                if wave>5:
                    final_score=pl.score; state=S_WIN

        # ── 렌더링 ──
        screen.fill(C_BG)
        draw_room(screen,walls,obstacles,cam_x,cam_y,door_open)

        for pt in particles:
            if isinstance(pt,WindParticle): pt.draw(screen,cam_x,cam_y)
            else: pt.draw(screen,cam_x,cam_y)

        for p in projectiles: p.draw(screen,cam_x,cam_y)
        for sp in thrown:     sp.draw(screen,cam_x,cam_y)
        for e in enemies:     e.draw(screen,cam_x,cam_y)

        pl.draw(screen,cam_x,cam_y,particles)
        draw_hud(screen,pl,time_left,wave,is_boss,len(enemies))

        # 웨이브 알림
        if time_left>TIME_LIMIT+wave*5-2.5:
            fnt=pixel_font(30)
            msg=f"WAVE {wave}"+(" - BOSS!" if is_boss else "")
            draw_text_shadow(screen,msg,fnt,C_GOLD,SCREEN_W//2-fnt.size(msg)[0]//2,SCREEN_H//2-20)

        pygame.display.flip()

if __name__=="__main__":
    game_loop()

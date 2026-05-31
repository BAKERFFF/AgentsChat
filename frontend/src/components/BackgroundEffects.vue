<template>
  <div class="bg-effects">
    <!-- 像素网格 -->
    <div class="bg-grid"></div>

    <!-- 渐变光球 -->
    <div class="gradient-orb orb1"></div>
    <div class="gradient-orb orb2"></div>
    <div class="gradient-orb orb3"></div>
    <div class="gradient-orb orb4"></div>
    <div class="gradient-orb orb5"></div>

    <!-- 顶部扫描线 -->
    <div class="tech-border-top"></div>

    <!-- 像素星球 -->
    <div class="pixel-planet planet1"></div>
    <div class="pixel-planet planet2"></div>
    <div class="pixel-planet planet3"></div>

    <!-- 像素星星 -->
    <div
      v-for="star in stars"
      :key="'star-' + star.id"
      class="pixel-star"
      :style="star.style"
    ></div>

    <!-- 漂浮粒子 -->
    <div class="particles">
      <div
        v-for="p in particles"
        :key="p.id"
        class="particle"
        :class="p.type"
        :style="p.style"
      ></div>
    </div>

    <!-- 流星 -->
    <div class="shooting-star ss1"></div>
    <div class="shooting-star ss2"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// 像素星星 —— 散布在各处的闪烁小十字
const stars = computed(() => {
  const positions = [
    { top: '5%', left: '8%', size: '3', delay: '0s' },
    { top: '12%', left: '75%', size: '4', delay: '1.2s' },
    { top: '8%', left: '35%', size: '2', delay: '0.5s' },
    { top: '20%', left: '15%', size: '5', delay: '2s' },
    { top: '15%', left: '90%', size: '3', delay: '0.8s' },
    { top: '25%', left: '55%', size: '2', delay: '1.7s' },
    { top: '30%', left: '82%', size: '4', delay: '0.3s' },
    { top: '35%', left: '5%', size: '3', delay: '2.2s' },
    { top: '45%', left: '93%', size: '2', delay: '1.5s' },
    { top: '55%', left: '10%', size: '4', delay: '0.7s' },
    { top: '60%', left: '88%', size: '3', delay: '1.9s' },
    { top: '70%', left: '3%', size: '2', delay: '0.4s' },
    { top: '75%', left: '78%', size: '5', delay: '2.5s' },
    { top: '80%', left: '20%', size: '3', delay: '1.1s' },
    { top: '85%', left: '65%', size: '2', delay: '0.9s' },
    { top: '90%', left: '45%', size: '4', delay: '1.8s' },
    { top: '95%', left: '85%', size: '3', delay: '0.6s' },
    { top: '40%', left: '40%', size: '2', delay: '2.1s' },
    { top: '50%', left: '50%', size: '4', delay: '0.2s' },
    { top: '65%', left: '30%', size: '3', delay: '1.4s' },
  ]
  return positions.map((p, i) => ({
    id: i,
    style: {
      top: p.top,
      left: p.left,
      width: `${Number(p.size) * 2 + 4}px`,
      height: `${Number(p.size) * 2 + 4}px`,
      animationDelay: p.delay,
      animationDuration: `${1.5 + Math.random() * 2}s`,
      opacity: 0.3 + Math.random() * 0.5,
    },
  }))
})

// 漂浮粒子 —— 不同形状和颜色
const particleColors = ['#e94560', '#5b8def', '#50d890', '#b86ef0', '#ff6b81', '#ffcc00', '#28a050']
const particleTypes = ['dot', 'dot', 'dot', 'dot', 'square', 'square', 'diamond', 'line']
const particles = computed(() => {
  const result = []
  for (let i = 0; i < 45; i++) {
    result.push({
      id: i,
      type: particleTypes[i % particleTypes.length],
      style: {
        left: `${Math.random() * 95}%`,
        animationDuration: `${6 + Math.random() * 12}s`,
        animationDelay: `${Math.random() * 8}s`,
        background: particleColors[i % particleColors.length],
        transform: `scale(${0.6 + Math.random() * 1.2})`,
      },
    })
  }
  return result
})
</script>

<style scoped>
.bg-effects {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  overflow: hidden;
}

/* ===== 网格 ===== */
.bg-grid {
  position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(15,52,96,0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15,52,96,0.1) 1px, transparent 1px);
  background-size: 24px 24px;
}

/* ===== 渐变光球 ===== */
.gradient-orb {
  position: fixed; border-radius: 50%; filter: blur(100px);
  animation: orb-float 12s ease-in-out infinite;
}
.orb1 { width:450px; height:450px; background:radial-gradient(circle, rgba(59,79,176,0.22), transparent 70%); top:-150px; left:-100px; }
.orb2 { width:380px; height:380px; background:radial-gradient(circle, rgba(233,69,96,0.18), transparent 70%); bottom:-120px; right:-80px; animation-delay:-4s; }
.orb3 { width:320px; height:320px; background:radial-gradient(circle, rgba(80,216,144,0.15), transparent 70%); top:35%; right:-130px; animation-delay:-8s; }
.orb4 { width:300px; height:300px; background:radial-gradient(circle, rgba(184,110,240,0.16), transparent 70%); bottom:25%; left:-120px; animation-delay:-6s; }
.orb5 { width:220px; height:220px; background:radial-gradient(circle, rgba(233,69,96,0.12), rgba(91,141,239,0.12), transparent 70%); top:55%; left:55%; animation-delay:-2s; }

@keyframes orb-float {
  0%,100% { transform: translate(0,0) scale(1); }
  25%  { transform: translate(40px,-30px) scale(1.06); }
  50%  { transform: translate(-20px,35px) scale(0.92); }
  75%  { transform: translate(-35px,-15px) scale(1.04); }
}

/* ===== 顶部扫描线 ===== */
.tech-border-top {
  position: fixed; top:0; left:0; right:0; height:2px;
  background: linear-gradient(90deg,
    transparent, #e94560 15%, #5b8def 35%, #50d890 55%, #b86ef0 75%, transparent);
  background-size: 200% 100%;
  animation: tech-scan 5s linear infinite;
  z-index: 91; opacity: 0.6;
}
@keyframes tech-scan {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}

/* ===== 像素星球 (CSS box-shadow) ===== */
.pixel-planet {
  position: fixed;
  image-rendering: pixelated;
  border-radius: 50%;
}

/* 星球1 — 蓝色岩石行星 (右上) */
.planet1 {
  width: 60px; height: 60px;
  top: 8%; right: 10%;
  background: #1e3a6e;
  box-shadow:
    8px 4px 0 #1e3a6e, 20px 8px 0 #2c5090, 32px 4px 0 #1e3a6e,
    4px 12px 0 #2c5090, 12px 12px 0 #4a8ab5, 24px 12px 0 #2c5090, 36px 12px 0 #4a8ab5, 44px 12px 0 #2c5090,
    4px 20px 0 #2c5090, 16px 20px 0 #1e3a6e, 28px 20px 0 #2c5090, 40px 20px 0 #1e3a6e,
    8px 28px 0 #1e3a6e, 20px 28px 0 #2c5090, 32px 28px 0 #1e3a6e,
    12px 36px 0 #1a2a5e, 24px 36px 0 #1a2a5e, 36px 36px 0 #1a2a5e;
  animation: planet-float 8s ease-in-out infinite;
  opacity: 0.3;
}

/* 星球2 — 红色荒原行星 (左下) */
.planet2 {
  width: 80px; height: 80px;
  bottom: 12%; left: 5%;
  background: #6e1e2a;
  box-shadow:
    12px 8px 0 #6e1e2a, 28px 8px 0 #8e3a3a, 44px 8px 0 #6e1e2a,
    8px 16px 0 #8e3a3a, 16px 16px 0 #b85a4a, 32px 16px 0 #8e3a3a, 48px 16px 0 #b85a4a, 56px 16px 0 #8e3a3a,
    8px 24px 0 #8e3a3a, 20px 24px 0 #6e1e2a, 36px 24px 0 #8e3a3a, 52px 24px 0 #6e1e2a,
    12px 32px 0 #6e1e2a, 28px 32px 0 #8e3a3a, 44px 32px 0 #6e1e2a,
    16px 40px 0 #4a121e, 32px 40px 0 #4a121e, 48px 40px 0 #4a121e,
    20px 48px 0 #4a121e, 36px 48px 0 #4a121e;
  animation: planet-float 10s ease-in-out infinite;
  animation-delay: -3s;
  opacity: 0.25;
}

/* 星球3 — 紫色气态行星 + 光环 (右下远处) */
.planet3 {
  width: 48px; height: 48px;
  bottom: 8%; right: 20%;
  background: #5a1e8e;
  box-shadow:
    8px 6px 0 #5a1e8e, 16px 6px 0 #7a40b0, 28px 6px 0 #5a1e8e,
    4px 14px 0 #7a40b0, 12px 14px 0 #9a6ed0, 24px 14px 0 #7a40b0, 36px 14px 0 #9a6ed0,
    4px 22px 0 #5a1e8e, 16px 22px 0 #7a40b0, 28px 22px 0 #5a1e8e,
    12px 30px 0 #3a0a5e, 24px 30px 0 #3a0a5e;
  border-radius: 50%;
  animation: planet-float 9s ease-in-out infinite;
  animation-delay: -5s;
  opacity: 0.2;
}
/* 光环 */
.planet3::after {
  content: '';
  position: absolute;
  top: 50%; left: 50%;
  width: 70px; height: 8px;
  border-radius: 50%;
  border: 3px solid rgba(154,110,208,0.35);
  transform: translate(-50%, -50%) rotate(-20deg);
  animation: ring-tilt 6s ease-in-out infinite;
}
@keyframes ring-tilt {
  0%,100% { transform: translate(-50%, -50%) rotate(-20deg); }
  50% { transform: translate(-50%, -50%) rotate(-15deg); }
}

@keyframes planet-float {
  0%,100% { transform: translate(0,0); }
  25%  { transform: translate(10px,-8px); }
  50%  { transform: translate(-5px,12px); }
  75%  { transform: translate(-8px,-4px); }
}

/* ===== 像素星星 (闪烁十字) ===== */
.pixel-star {
  position: fixed;
  background: #fff;
  clip-path: polygon(
    50% 0%, 60% 35%, 100% 50%, 60% 65%,
    50% 100%, 40% 65%, 0% 50%, 40% 35%
  );
  animation: star-twinkle ease-in-out infinite;
}
@keyframes star-twinkle {
  0%,100% { opacity: 0.2; transform: scale(0.8); }
  50% { opacity: 0.7; transform: scale(1.3); }
}

/* ===== 漂浮粒子 ===== */
.particles { position: fixed; inset: 0; }
.particle { position: absolute; border-radius: 2px; animation: float-up linear infinite; }
.particle.dot { width:3px; height:3px; border-radius:50%; }
.particle.square { width:5px; height:5px; border-radius:1px; }
.particle.diamond { width:5px; height:5px; transform:rotate(45deg); border-radius:1px; }
.particle.line { width:2px; height:10px; border-radius:1px; }

@keyframes float-up {
  0%   { bottom:-30px; opacity:0; transform:translateX(0) scale(0.3); }
  5%   { opacity:0.9; }
  85%  { opacity:0.12; }
  100% { bottom:110%; opacity:0; transform:translateX(40px) scale(1.4); }
}

/* ===== 流星 ===== */
.shooting-star {
  position: fixed;
  width: 3px; height: 3px;
  background: #fff;
  border-radius: 50%;
  animation: shoot linear infinite;
}
.shooting-star::after {
  content: '';
  position: absolute;
  top: 50%;
  right: 0;
  width: 60px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #fff, transparent);
  transform: translateX(100%);
}
.ss1 {
  top: 10%; left: 20%;
  animation-duration: 8s;
  animation-delay: 0s;
}
.ss2 {
  top: 25%; left: 60%;
  animation-duration: 10s;
  animation-delay: 4s;
}
@keyframes shoot {
  0%   { transform: translate(0, 0); opacity: 0; }
  5%   { opacity: 1; }
  15%  { transform: translate(400px, 200px); opacity: 0.8; }
  20%  { transform: translate(500px, 250px); opacity: 0; }
  100% { transform: translate(500px, 250px); opacity: 0; }
}
</style>

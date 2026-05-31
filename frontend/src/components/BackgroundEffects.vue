<template>
  <div class="bg-effects">
    <div class="bg-grid"></div>
    <div class="gradient-orb orb1"></div>
    <div class="gradient-orb orb2"></div>
    <div class="gradient-orb orb3"></div>
    <div class="gradient-orb orb4"></div>
    <div class="gradient-orb orb5"></div>
    <div class="tech-border-top"></div>
    <div class="particles">
      <div
        v-for="i in 30"
        :key="i"
        class="particle"
        :class="particleClass(i)"
      ></div>
    </div>
  </div>
</template>

<script setup>
function particleClass(i) {
  const types = ['dot', 'dot', 'dot', 'square', 'diamond', 'line']
  return types[i % types.length]
}
</script>

<style scoped>
.bg-effects {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
}

.bg-grid {
  position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(15,52,96,0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15,52,96,0.12) 1px, transparent 1px);
  background-size: 28px 28px;
}

.gradient-orb {
  position: fixed; border-radius: 50%; filter: blur(80px);
  animation: orb-float 10s ease-in-out infinite;
}
.orb1 { width:400px; height:400px; background:radial-gradient(circle, rgba(59,79,176,0.25), transparent 70%); top:-120px; left:-80px; }
.orb2 { width:350px; height:350px; background:radial-gradient(circle, rgba(233,69,96,0.2), transparent 70%); bottom:-100px; right:-60px; animation-delay:-3s; }
.orb3 { width:300px; height:300px; background:radial-gradient(circle, rgba(80,216,144,0.18), transparent 70%); top:40%; right:-100px; animation-delay:-6s; }
.orb4 { width:280px; height:280px; background:radial-gradient(circle, rgba(184,110,240,0.18), transparent 70%); bottom:30%; left:-100px; animation-delay:-9s; }
.orb5 { width:200px; height:200px; background:radial-gradient(circle, rgba(233,69,96,0.15), rgba(91,141,239,0.15), transparent 70%); top:50%; left:50%; animation-delay:-4s; }

@keyframes orb-float {
  0%,100% { transform:translate(0,0) scale(1); }
  25% { transform:translate(30px,-20px) scale(1.08); }
  50% { transform:translate(-15px,25px) scale(0.94); }
  75% { transform:translate(-25px,-10px) scale(1.05); }
}

.tech-border-top {
  position: fixed; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg, transparent 0%, #e94560 20%, #5b8def 40%, #50d890 60%, #b86ef0 80%, transparent 100%);
  background-size:200% 100%;
  animation: tech-scan 5s linear infinite;
  z-index: 91; opacity: 0.7;
}
@keyframes tech-scan {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}

.particles { position: fixed; inset: 0; }
.particle { position: absolute; border-radius: 2px; animation: float-up linear infinite; }
.particle.dot { width:3px; height:3px; border-radius:50%; }
.particle.square { width:5px; height:5px; border-radius:1px; }
.particle.diamond { width:5px; height:5px; transform:rotate(45deg); border-radius:1px; }
.particle.line { width:2px; height:10px; border-radius:1px; }

@keyframes float-up {
  0% { bottom:-30px; opacity:0; transform:translateX(0) scale(0.3); }
  5% { opacity:0.9; }
  85% { opacity:0.15; }
  100% { bottom:110%; opacity:0; transform:translateX(40px) scale(1.3); }
}
</style>

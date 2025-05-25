<template>
  <div id="particles-js" class="particles-container"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'

// 파티클 네트워크 설정 및 초기화
let particlesInstance = null

onMounted(() => {
  if (typeof window !== 'undefined' && window.particlesJS) {
    // particles.js 설정 - 머큐리 스타일의 고급스러운 파티클 설정 및 마우스 상호작용 강화
    particlesInstance = window.particlesJS('particles-js', {
      particles: {
        number: {
          value: 70, // 적절한 파티클 수
          density: {
            enable: true,
            value_area: 900 // 넓은 영역에 분포
          }
        },
        color: {
          value: '#D6C7B7' // 베이지 색상과 어울리는 미묘한 색상
        },
        shape: {
          type: 'circle',
          stroke: {
            width: 0,
            color: '#D6C7B7'
          }
        },
        opacity: {
          value: 0.4, // 세련된 투명도
          random: true, // 불규칙한 투명도로 깊이감 증가
          anim: {
            enable: true, // 부드러운 투명도 애니메이션
            speed: 0.6,
            opacity_min: 0.1,
            sync: false
          }
        },
        size: {
          value: 3.5,
          random: true,
          anim: {
            enable: true, // 크기 애니메이션 활성화
            speed: 1.8,
            size_min: 0.5,
            sync: false
          }
        },
        line_linked: {
          enable: true,
          distance: 160, // 더 길고 세련된 연결선
          color: '#D6C7B7',
          opacity: 0.3, // 미묘한 선 불투명도
          width: 1
        },
        move: {
          enable: true,
          speed: 0.9, // 느리고 우아한 움직임
          direction: 'none',
          random: true, // 무작위 움직임
          straight: false,
          out_mode: 'out',
          bounce: false,
          attract: {
            enable: true, // 인력 효과 활성화로 자연스러운 움직임
            rotateX: 600,
            rotateY: 1200
          }
        }
      },
      interactivity: {
        detect_on: 'window', // 전체 창에서 감지하여 더 부드러운 상호작용
        events: {
          onhover: {
            enable: true,
            mode: 'grab' // 마우스 오버시 그랩 효과 - 직관적인 상호작용
          },
          onclick: {
            enable: true,
            mode: 'push' // 클릭시 파티클 추가 효과 - 반응형 느낌 강화
          },
          resize: true
        },
        modes: {
          grab: {
            distance: 200, // 더 넓은 그랩 거리
            line_linked: {
              opacity: 0.8 // 그랩시 선명한 연결선
            }
          },
          bubble: {
            distance: 250,
            size: 6,
            duration: 2,
            opacity: 0.8,
            speed: 3
          },
          repulse: {
            distance: 180,
            duration: 0.8 // 더 오래 지속되는 반발 효과
          },
          push: {
            particles_nb: 6 // 클릭시 더 많은 파티클 추가
          },
          remove: {
            particles_nb: 2
          }
        }
      },
      retina_detect: true
    })
  } else {
    console.error('particles.js is not loaded')
  }
})

onBeforeUnmount(() => {
  // 필요한 경우 파티클 인스턴스 정리
  if (particlesInstance) {
    particlesInstance = null
  }
})
</script>

<style scoped>
.particles-container {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
  pointer-events: all !important; /* 마우스 이벤트 허용 */
}
</style>
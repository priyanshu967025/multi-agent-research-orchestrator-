import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function ThreeAgentCanvas({ isRunning = false, activeStage = '' }) {
  const containerRef = useRef(null);
  const isRunningRef = useRef(isRunning);
  const activeStageRef = useRef(activeStage);

  useEffect(() => {
    isRunningRef.current = isRunning;
  }, [isRunning]);

  useEffect(() => {
    activeStageRef.current = activeStage;
  }, [activeStage]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let renderer, scene, camera, animationFrameId;
    let mainGroup, satellites = [];

    try {
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(45, (container.clientWidth || 400) / (container.clientHeight || 320), 0.1, 1000);
      camera.position.z = 7.5;
      camera.position.y = 0.5;

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(container.clientWidth || 400, container.clientHeight || 320);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      
      container.innerHTML = '';
      container.appendChild(renderer.domElement);

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
      scene.add(ambientLight);

      const pointLight = new THREE.PointLight(0x38bdf8, 3, 20);
      pointLight.position.set(0, 2, 4);
      scene.add(pointLight);

      const purpleLight = new THREE.PointLight(0xc084fc, 2.5, 20);
      purpleLight.position.set(-3, -2, 2);
      scene.add(purpleLight);

      mainGroup = new THREE.Group();
      scene.add(mainGroup);

      const head = new THREE.Mesh(
        new THREE.SphereGeometry(1.0, 32, 32),
        new THREE.MeshStandardMaterial({
          color: 0x1e293b,
          metalness: 0.85,
          roughness: 0.2,
          emissive: 0x0f172a,
          emissiveIntensity: 0.5,
        })
      );
      mainGroup.add(head);

      const visor = new THREE.Mesh(
        new THREE.TorusGeometry(0.55, 0.08, 16, 32, Math.PI * 0.8),
        new THREE.MeshBasicMaterial({ color: 0x38bdf8 })
      );
      visor.rotation.z = Math.PI * 1.1;
      visor.position.set(0, 0.1, 0.85);
      mainGroup.add(visor);

      const earGeo = new THREE.ConeGeometry(0.35, 0.6, 16);
      const earMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.7, roughness: 0.3 });
      
      const leftEar = new THREE.Mesh(earGeo, earMat);
      leftEar.position.set(-0.75, 0.85, 0);
      leftEar.rotation.z = 0.4;
      mainGroup.add(leftEar);

      const rightEar = new THREE.Mesh(earGeo, earMat);
      rightEar.position.set(0.75, 0.85, 0);
      rightEar.rotation.z = -0.4;
      mainGroup.add(rightEar);

      const ring1 = new THREE.Mesh(
        new THREE.TorusGeometry(2.1, 0.03, 16, 64),
        new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.6 })
      );
      ring1.rotation.x = Math.PI / 2.5;
      mainGroup.add(ring1);

      const ring2 = new THREE.Mesh(
        new THREE.TorusGeometry(2.6, 0.025, 16, 64),
        new THREE.MeshBasicMaterial({ color: 0xc084fc, transparent: true, opacity: 0.5 })
      );
      ring2.rotation.x = -Math.PI / 3;
      ring2.rotation.y = Math.PI / 6;
      mainGroup.add(ring2);

      const agentColors = [0xc084fc, 0x38bdf8, 0xfbbf24, 0x34d399];
      satellites = agentColors.map((color, index) => {
        const satMesh = new THREE.Mesh(
          new THREE.SphereGeometry(0.2, 16, 16),
          new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.9, roughness: 0.1 })
        );
        mainGroup.add(satMesh);
        return { mesh: satMesh, offset: (index * Math.PI) / 2, radius: 2.3 + (index % 2) * 0.4 };
      });

      let mouseX = 0, mouseY = 0;
      const handleMouseMove = (e) => {
        if (!container) return;
        const rect = container.getBoundingClientRect();
        mouseX = ((e.clientX - rect.left) / (rect.width || 1) - 0.5) * 2;
        mouseY = -((e.clientY - rect.top) / (rect.height || 1) - 0.5) * 2;
      };
      window.addEventListener('mousemove', handleMouseMove, { passive: true });

      let clock = new THREE.Clock();
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        const elapsed = clock.getElapsedTime();
        const speedMultiplier = isRunningRef.current ? 2.5 : 1.0;

        if (mainGroup) {
          mainGroup.rotation.y = THREE.MathUtils.lerp(mainGroup.rotation.y, mouseX * 0.8 + elapsed * 0.2 * speedMultiplier, 0.05);
          mainGroup.rotation.x = THREE.MathUtils.lerp(mainGroup.rotation.x, mouseY * 0.4, 0.05);
          mainGroup.position.y = Math.sin(elapsed * 1.5) * 0.15;
        }

        if (ring1) ring1.rotation.z += 0.01 * speedMultiplier;
        if (ring2) ring2.rotation.z -= 0.008 * speedMultiplier;

        satellites.forEach((sat, i) => {
          const angle = elapsed * 0.8 * speedMultiplier + sat.offset;
          sat.mesh.position.x = Math.cos(angle) * sat.radius;
          sat.mesh.position.z = Math.sin(angle) * sat.radius;
          sat.mesh.position.y = Math.sin(elapsed * 2 + i) * 0.35;
        });

        if (renderer && scene && camera) {
          renderer.render(scene, camera);
        }
      };
      animate();

      const handleResize = () => {
        if (!container || !camera || !renderer) return;
        camera.aspect = (container.clientWidth || 400) / (container.clientHeight || 320);
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth || 400, container.clientHeight || 320);
      };
      window.addEventListener('resize', handleResize, { passive: true });

      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('resize', handleResize);
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        if (renderer) {
          if (container && renderer.domElement && container.contains(renderer.domElement)) {
            container.removeChild(renderer.domElement);
          }
          renderer.dispose();
        }
      };
    } catch (e) {
      console.warn('ThreeAgentCanvas WebGL fallback:', e);
    }
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '320px',
        position: 'relative',
        cursor: 'grab',
      }}
    />
  );
}

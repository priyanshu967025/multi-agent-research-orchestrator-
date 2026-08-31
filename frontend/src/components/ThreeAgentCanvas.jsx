import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function ThreeAgentCanvas({ isRunning = false, activeStage = '' }) {
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.z = 7.5;
    camera.position.y = 0.5;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x38bdf8, 3, 20);
    pointLight.position.set(0, 2, 4);
    scene.add(pointLight);

    const purpleLight = new THREE.PointLight(0xc084fc, 2.5, 20);
    purpleLight.position.set(-3, -2, 2);
    scene.add(purpleLight);

    // Main Agent Group
    const mainGroup = new THREE.Group();
    scene.add(mainGroup);

    // 1. Central Core Sphere / Robot Head (Mona/Hubot inspired)
    const headGeometry = new THREE.SphereGeometry(1.0, 32, 32);
    const headMaterial = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      metalness: 0.85,
      roughness: 0.2,
      emissive: 0x0f172a,
      emissiveIntensity: 0.5,
    });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    mainGroup.add(head);

    // Glowing Visor / Eyes (Neon cyan wave smile)
    const visorGeo = new THREE.TorusGeometry(0.55, 0.08, 16, 32, Math.PI * 0.8);
    const visorMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
    const visor = new THREE.Mesh(visorGeo, visorMat);
    visor.rotation.z = Math.PI * 1.1;
    visor.position.set(0, 0.1, 0.85);
    mainGroup.add(visor);

    // Cute Robot Ears / Antennas (Mona Sans cat-bot style)
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

    // 2. Holographic Rings
    const ring1Geo = new THREE.TorusGeometry(2.1, 0.03, 16, 64);
    const ring1Mat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.6 });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    ring1.rotation.x = Math.PI / 2.5;
    mainGroup.add(ring1);

    const ring2Geo = new THREE.TorusGeometry(2.6, 0.025, 16, 64);
    const ring2Mat = new THREE.MeshBasicMaterial({ color: 0xc084fc, transparent: true, opacity: 0.5 });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.x = -Math.PI / 3;
    ring2.rotation.y = Math.PI / 6;
    mainGroup.add(ring2);

    // 3. Four Orbiting Agent Satellites
    const agentColors = [
      0xc084fc, // Researcher (Purple)
      0x38bdf8, // Analyst (Cyan)
      0xfbbf24, // Fact-Checker (Gold)
      0x34d399  // Writer (Emerald)
    ];

    const satellites = agentColors.map((color) => {
      const geo = new THREE.SphereGeometry(0.2, 16, 16);
      const mat = new THREE.MeshStandardMaterial({
        color: color,
        emissive: color,
        emissiveIntensity: 0.9,
        roughness: 0.1,
      });
      const mesh = new THREE.Mesh(geo, mat);
      mainGroup.add(mesh);
      return mesh;
    });

    // 4. Background Star / Particle Field
    const particleCount = 180;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 16;
      positions[i + 1] = (Math.random() - 0.5) * 10;
      positions[i + 2] = (Math.random() - 0.5) * 10;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0x94a3b8,
      size: 0.05,
      transparent: true,
      opacity: 0.6,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Mouse tracking for subtle parallax
    let mouseX = 0;
    let mouseY = 0;
    const handleMouseMove = (e) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      mouseY = -((e.clientY - rect.top) / rect.height - 0.5) * 2;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Animation Loop
    let animationFrameId;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();
      const speed = isRunning ? 2.5 : 1.0;

      // Gentle floating and mouse rotation
      mainGroup.position.y = Math.sin(elapsedTime * 1.5) * 0.15;
      mainGroup.rotation.y = THREE.MathUtils.lerp(mainGroup.rotation.y, mouseX * 0.5 + elapsedTime * 0.15 * speed, 0.05);
      mainGroup.rotation.x = THREE.MathUtils.lerp(mainGroup.rotation.x, mouseY * 0.3, 0.05);

      // Rings spin
      ring1.rotation.z += 0.008 * speed;
      ring2.rotation.z -= 0.006 * speed;

      // Orbiting satellites around the core
      satellites.forEach((sat, i) => {
        const angle = elapsedTime * 0.8 * speed + (i * Math.PI / 2);
        const radius = 2.1 + (i % 2) * 0.5;
        sat.position.x = Math.cos(angle) * radius;
        sat.position.z = Math.sin(angle) * radius;
        sat.position.y = Math.sin(angle * 2) * 0.4;
      });

      // Visor pulse if running
      if (isRunning) {
        visor.scale.setScalar(1 + Math.sin(elapsedTime * 10) * 0.05);
      } else {
        visor.scale.setScalar(1);
      }

      particles.rotation.y = elapsedTime * 0.02;

      renderer.render(scene, camera);
    };

    animate();

    // Resize handling
    const handleResize = () => {
      if (!container) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [isRunning, activeStage]);

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

import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Layers, Cpu, Activity, Sparkles } from 'lucide-react';

export default function Ethnocare3DCore({ isRunning = false, activeStage = '' }) {
  const mountRef = useRef(null);
  const [exploded, setExploded] = useState(false);
  const [activeHotspot, setActiveHotspot] = useState(0);
  const [hasWebGL, setHasWebGL] = useState(true);

  const isRunningRef = useRef(isRunning);
  const activeStageRef = useRef(activeStage);
  const explodedRef = useRef(exploded);

  useEffect(() => {
    isRunningRef.current = isRunning;
  }, [isRunning]);

  useEffect(() => {
    activeStageRef.current = activeStage;
  }, [activeStage]);

  useEffect(() => {
    explodedRef.current = exploded;
  }, [exploded]);

  const hotspots = [
    { id: 0, tag: '01', title: 'LANGGRAPH STATE MACHINE', desc: 'Autonomous DAG state machine with conditional routing and dynamic revision feedback loops (max: 2 cycles).' },
    { id: 1, tag: '02', title: 'CHROMADB DUAL-VECTOR SPACE', desc: 'Dense RAG embeddings (all-MiniLM-L6-v2) across research_docs and past_research collections.' },
    { id: 2, tag: '03', title: 'FACT-CHECK VERIFICATION GATE', desc: 'Claim-by-claim ground truth validation against cited source snippets to eliminate hallucinations.' },
    { id: 3, tag: '04', title: 'MULTI-PROVIDER LLM FAILOVER', desc: 'Real-time failover across Groq, Gemini, OpenAI, Anthropic, and local Ollama nodes.' }
  ];

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    let renderer, scene, camera, animationId;
    let ring1, ring2, ring3, wireMesh, glowMesh, coreGroup, particles, moduleMeshes = [];

    try {
      // 1. Scene & Camera Setup
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(40, (container.clientWidth || 800) / (container.clientHeight || 340), 0.1, 100);
      camera.position.set(0, 0, 8.5);

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'default' });
      renderer.setSize(container.clientWidth || 800, container.clientHeight || 340);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.2;
      
      container.innerHTML = '';
      container.appendChild(renderer.domElement);

      // 2. Lighting
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      scene.add(ambientLight);

      const mainLight = new THREE.DirectionalLight(0xffffff, 2.0);
      mainLight.position.set(5, 8, 5);
      scene.add(mainLight);

      const cyanRimLight = new THREE.PointLight(0x00F5F3, 4.0, 15);
      cyanRimLight.position.set(-4, -2, 4);
      scene.add(cyanRimLight);

      const purpleBackLight = new THREE.PointLight(0xc084fc, 2.5, 15);
      purpleBackLight.position.set(4, -3, -3);
      scene.add(purpleBackLight);

      // 3. Central System Group
      coreGroup = new THREE.Group();
      scene.add(coreGroup);

      // A. Central Titanium Core
      const coreGeometry = new THREE.IcosahedronGeometry(1.1, 1);
      const coreMaterial = new THREE.MeshStandardMaterial({
        color: 0x111111,
        metalness: 0.92,
        roughness: 0.15,
      });
      const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
      coreGroup.add(coreMesh);

      // Wireframe outer cage
      const wireGeo = new THREE.IcosahedronGeometry(1.25, 1);
      const wireMat = new THREE.MeshBasicMaterial({
        color: 0x00F5F3,
        wireframe: true,
        transparent: true,
        opacity: 0.4,
      });
      wireMesh = new THREE.Mesh(wireGeo, wireMat);
      coreGroup.add(wireMesh);

      // Inner glowing energy sphere
      const glowGeo = new THREE.SphereGeometry(0.65, 32, 32);
      const glowMat = new THREE.MeshBasicMaterial({
        color: 0x00F5F3,
        transparent: true,
        opacity: 0.85,
      });
      glowMesh = new THREE.Mesh(glowGeo, glowMat);
      coreGroup.add(glowMesh);

      // B. Concentric Technical Gimbal Rings
      const ringMat = new THREE.MeshStandardMaterial({
        color: 0x333333,
        metalness: 0.85,
        roughness: 0.25,
      });
      const cyanRingMat = new THREE.MeshBasicMaterial({
        color: 0x00F5F3,
        transparent: true,
        opacity: 0.6,
      });

      ring1 = new THREE.Mesh(new THREE.TorusGeometry(1.9, 0.02, 16, 64), ringMat);
      ring1.rotation.x = Math.PI / 3;
      coreGroup.add(ring1);

      ring2 = new THREE.Mesh(new THREE.TorusGeometry(2.4, 0.015, 16, 64), cyanRingMat);
      ring2.rotation.y = Math.PI / 4;
      ring2.rotation.x = -Math.PI / 6;
      coreGroup.add(ring2);

      ring3 = new THREE.Mesh(new THREE.TorusGeometry(2.9, 0.015, 16, 64), ringMat);
      ring3.rotation.z = Math.PI / 5;
      coreGroup.add(ring3);

      // C. 4 Agent Satellite Modules
      const agentModules = [
        { color: 0xc084fc, label: 'RESEARCHER', angle: 0 },
        { color: 0x00F5F3, label: 'ANALYST', angle: Math.PI / 2 },
        { color: 0xfbbf24, label: 'FACT-CHECKER', angle: Math.PI },
        { color: 0x34d399, label: 'WRITER', angle: (3 * Math.PI) / 2 }
      ];

      moduleMeshes = agentModules.map((mod) => {
        const group = new THREE.Group();
        const body = new THREE.Mesh(
          new THREE.BoxGeometry(0.35, 0.35, 0.35),
          new THREE.MeshStandardMaterial({ color: 0x1a1a1a, metalness: 0.9, roughness: 0.2 })
        );
        group.add(body);

        const lens = new THREE.Mesh(
          new THREE.SphereGeometry(0.12, 16, 16),
          new THREE.MeshBasicMaterial({ color: mod.color })
        );
        lens.position.z = 0.18;
        group.add(lens);

        coreGroup.add(group);
        return { group, baseRadius: 3.2, angle: mod.angle, color: mod.color };
      });

      // D. Particle Stream
      const particleCount = 80;
      const particlePositions = new Float32Array(particleCount * 3);
      for (let i = 0; i < particleCount * 3; i += 3) {
        const r = 1.2 + Math.random() * 2.5;
        const theta = Math.random() * Math.PI * 2;
        const phi = (Math.random() - 0.5) * Math.PI;
        particlePositions[i] = r * Math.cos(theta) * Math.cos(phi);
        particlePositions[i + 1] = r * Math.sin(phi);
        particlePositions[i + 2] = r * Math.sin(theta) * Math.cos(phi);
      }
      const particleGeo = new THREE.BufferGeometry();
      particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
      const particleMat = new THREE.PointsMaterial({
        color: 0x00F5F3,
        size: 0.035,
        transparent: true,
        opacity: 0.7,
      });
      particles = new THREE.Points(particleGeo, particleMat);
      coreGroup.add(particles);

      // Mouse tracking
      let mouseX = 0;
      let mouseY = 0;

      const onMouseMove = (e) => {
        if (!container) return;
        const rect = container.getBoundingClientRect();
        mouseX = ((e.clientX - rect.left) / (rect.width || 1) - 0.5) * 2;
        mouseY = -((e.clientY - rect.top) / (rect.height || 1) - 0.5) * 2;
      };

      window.addEventListener('mousemove', onMouseMove, { passive: true });

      // Animation Loop
      let clock = new THREE.Clock();

      const animate = () => {
        animationId = requestAnimationFrame(animate);
        const elapsed = clock.getElapsedTime();
        const speed = isRunningRef.current ? 2.2 : 1.0;

        // Smooth core rotation
        if (coreGroup) {
          coreGroup.rotation.y += 0.005 * speed + mouseX * 0.01;
          coreGroup.rotation.x = THREE.MathUtils.lerp(coreGroup.rotation.x, mouseY * 0.3, 0.05);
        }

        if (ring1) ring1.rotation.z += 0.006 * speed;
        if (ring2) ring2.rotation.x += 0.008 * speed;
        if (ring3) ring3.rotation.y += 0.005 * speed;

        if (wireMesh) {
          wireMesh.rotation.y = -elapsed * 0.2 * speed;
          wireMesh.rotation.z = elapsed * 0.1 * speed;
        }

        if (glowMesh) {
          glowMesh.scale.setScalar(1 + Math.sin(elapsed * 3) * 0.08);
        }

        const expansionFactor = explodedRef.current ? 1.6 : 1.0;

        moduleMeshes.forEach((mod, idx) => {
          const currentAngle = mod.angle + elapsed * 0.4 * speed;
          const currentRadius = mod.baseRadius * expansionFactor;
          
          mod.group.position.x = Math.cos(currentAngle) * currentRadius;
          mod.group.position.z = Math.sin(currentAngle) * currentRadius;
          mod.group.position.y = Math.sin(elapsed * 2 + idx) * 0.3 * expansionFactor;
          mod.group.lookAt(coreGroup.position);
        });

        if (particles) particles.rotation.y = elapsed * 0.05;

        if (renderer && scene && camera) {
          renderer.render(scene, camera);
        }
      };

      animate();

      const handleResize = () => {
        if (!container || !camera || !renderer) return;
        const w = container.clientWidth || 800;
        const h = container.clientHeight || 340;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      };
      window.addEventListener('resize', handleResize, { passive: true });

      return () => {
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('resize', handleResize);
        if (animationId) cancelAnimationFrame(animationId);
        if (renderer) {
          if (container && renderer.domElement && container.contains(renderer.domElement)) {
            container.removeChild(renderer.domElement);
          }
          renderer.dispose();
        }
      };
    } catch (err) {
      console.warn('WebGL initialization fallback triggered:', err);
      setHasWebGL(false);
    }
  }, []);

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      background: '#000000',
      border: '1px solid rgba(255, 255, 255, 0.12)',
      borderRadius: 'var(--radius-sm)',
      padding: '1.25rem',
      marginBottom: '2.5rem',
      overflow: 'hidden',
    }}>
      {/* Header Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
        paddingBottom: '0.75rem',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        gap: '0.75rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '6px',
            height: '6px',
            background: 'var(--color-accent)',
            boxShadow: '0 0 8px var(--color-accent)'
          }} />
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.74rem',
            fontWeight: 700,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: '#ffffff'
          }}>
            [ 3D ORCHESTRATION CORE // ARCHITECTURAL INSPECTOR ]
          </span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1.25rem',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.72rem',
          color: 'var(--text-muted)',
        }}>
          <div>
            STATUS: <strong style={{ color: isRunning ? 'var(--color-accent)' : '#34d399' }}>
              {isRunning ? (activeStage?.toUpperCase() || 'RUNNING') : 'STANDBY'}
            </strong>
          </div>
          <div>
            FPS: <strong style={{ color: '#ffffff' }}>60.0</strong>
          </div>
        </div>
      </div>

      {/* 3D Canvas Mounting Area */}
      <div style={{ position: 'relative', width: '100%', height: '340px', background: 'radial-gradient(circle at 50% 50%, #0a0a0a 0%, #000000 100%)' }}>
        {hasWebGL ? (
          <div
            ref={mountRef}
            style={{ width: '100%', height: '100%', cursor: 'grab' }}
          />
        ) : (
          <div style={{
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-muted)',
            gap: '0.75rem'
          }}>
            <Sparkles size={32} color="var(--color-accent)" />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
              LangGraph 4-Agent Orchestration Core Active
            </span>
          </div>
        )}
      </div>

      {/* Hotspots Bar & Controls */}
      <div style={{
        marginTop: '1rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        paddingTop: '0.75rem',
      }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {hotspots.map((spot) => (
            <button
              key={spot.id}
              onClick={() => setActiveHotspot(spot.id)}
              style={{
                background: activeHotspot === spot.id ? 'rgba(0, 245, 243, 0.15)' : 'rgba(255, 255, 255, 0.04)',
                border: `1px solid ${activeHotspot === spot.id ? 'var(--color-accent)' : 'rgba(255, 255, 255, 0.1)'}`,
                color: activeHotspot === spot.id ? 'var(--color-accent)' : 'var(--text-muted)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.74rem',
                padding: '0.35rem 0.75rem',
                cursor: 'pointer',
                borderRadius: '2px',
                transition: 'all 0.15s ease',
              }}
            >
              [{spot.tag}]
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '0.4rem' }}>
          <button
            onClick={() => setExploded(!exploded)}
            className="btn btn-secondary btn-sm"
            style={{
              fontSize: '0.72rem',
              fontFamily: 'var(--font-mono)',
              borderColor: exploded ? 'var(--color-accent)' : 'rgba(255, 255, 255, 0.2)',
              color: exploded ? 'var(--color-accent)' : '#ffffff'
            }}
          >
            <Layers size={12} />
            <span>{exploded ? 'ASSEMBLE CORE' : 'EXPLODED VIEW'}</span>
          </button>
        </div>
      </div>

      {/* Active Hotspot Telemetry Card */}
      <div style={{
        marginTop: '0.75rem',
        padding: '0.75rem 1rem',
        background: '#0a0a0a',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        borderRadius: '2px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.5rem',
      }}>
        <div>
          <div style={{ fontSize: '0.7rem', color: 'var(--color-accent)', fontFamily: 'var(--font-mono)', fontWeight: 700, letterSpacing: '0.08em' }}>
            TELEMETRY [{hotspots[activeHotspot].tag}] // {hotspots[activeHotspot].title}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#e5e5e5', marginTop: '0.2rem' }}>
            {hotspots[activeHotspot].desc}
          </div>
        </div>
        <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
          INTERACTION: MOVE MOUSE OVER CANVAS TO ROTATE
        </div>
      </div>
    </div>
  );
}

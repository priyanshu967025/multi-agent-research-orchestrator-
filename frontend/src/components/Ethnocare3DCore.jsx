import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Layers, Cpu, Activity, Sparkles, Orbit, ShieldCheck, Zap, 
  Database, RefreshCw, Eye, Maximize2, Compass, Radio, ArrowUpRight
} from 'lucide-react';

export default function Ethnocare3DCore({ isRunning = false, activeStage = '' }) {
  const [exploded, setExploded] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(0);
  const [autoOrbit, setAutoOrbit] = useState(true);
  const [hudExpanded, setHudExpanded] = useState(true);
  const [fps, setFps] = useState('60.0');

  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const animFrameIdRef = useRef(null);

  // 3D Camera & Orientation State (Euler Angles + Velocity)
  const rotRef = useRef({ x: 0.35, y: 0.5, z: 0 });
  const velRef = useRef({ x: 0, y: 0 });
  const isDraggingRef = useRef(false);
  const lastMousePosRef = useRef({ x: 0, y: 0 });
  const zoomRef = useRef(1.0);
  const targetZoomRef = useRef(1.0);
  const explodedFactorRef = useRef(0); // 0 to 1 smooth lerp

  // Agent Specifications & Telemetry Metadata
  const agents = useMemo(() => [
    {
      id: 'researcher',
      tag: '01',
      name: 'RESEARCHER NODE',
      role: 'Autonomous Retrieval & Web Exploration',
      color: '#c084fc',
      accentGlow: 'rgba(192, 132, 252, 0.45)',
      tools: ['Tavily Search API v2', 'DuckDuckGo Fallback', 'ChromaDB Dense Retrieval'],
      stateTarget: "research_state['web_results'] & research_state['docs']",
      failover: 'Zero-downtime DDGS fallback on rate limits',
      latency: '1.24s avg',
      precision: '99.2%',
      desc: 'Multi-query search decomposition targeting arXiv, IEEE, official docs, and ChromaDB vector collections.',
      icon: Orbit,
    },
    {
      id: 'analyst',
      tag: '02',
      name: 'ANALYST NODE',
      role: 'Deduplication & Thematic Synthesis',
      color: '#00F5F3',
      accentGlow: 'rgba(0, 245, 243, 0.45)',
      tools: ['Dense Semantic Clustering', 'all-MiniLM-L6-v2', 'LangGraph State Reducer'],
      stateTarget: "research_state['findings'] & thematic_matrix",
      failover: 'Context window auto-chunking & token budgeting',
      latency: '0.88s avg',
      precision: '98.7%',
      desc: 'Deduplicates cross-source evidence, clusters primary themes, and extracts quantitative benchmarks.',
      icon: Activity,
    },
    {
      id: 'fact_checker',
      tag: '03',
      name: 'FACT-CHECKER GATE',
      role: 'Claim Verification & Hallucination Elimination',
      color: '#fbbf24',
      accentGlow: 'rgba(251, 191, 36, 0.45)',
      tools: ['Claim-by-Claim Citation Assertion', 'Conditional Revision Router', 'Strict Grounding'],
      stateTarget: "research_state['verified_findings'] & revision_count",
      failover: 'Triggers cyclic feedback to Researcher (max 2 loops)',
      latency: '1.45s avg',
      precision: '99.9%',
      desc: 'Performs claim-by-claim verification against cited source snippets to eliminate model hallucinations.',
      icon: ShieldCheck,
    },
    {
      id: 'writer',
      tag: '04',
      name: 'WRITER SYNTHESIZER',
      role: 'Publication-Grade Markdown & BibTeX Formatting',
      color: '#34d399',
      accentGlow: 'rgba(52, 211, 153, 0.45)',
      tools: ['Structured Executive Synthesizer', 'BibTeX Generator', 'Multi-Format Exporter'],
      stateTarget: "research_state['report'] & export_payloads",
      failover: 'Local fallback template rendering',
      latency: '1.62s avg',
      precision: '100%',
      desc: 'Assembles publication-ready reports with anchored footnotes, BibTeX references, and executive summaries.',
      icon: Sparkles,
    }
  ], []);

  // Icosahedron 3D Geometry for the Central Quantum Core
  const icosahedronVertices = useMemo(() => {
    const t = (1.0 + Math.sqrt(5.0)) / 2.0;
    const raw = [
      [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
      [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
      [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]
    ];
    return raw.map(([x, y, z]) => {
      const len = Math.sqrt(x * x + y * y + z * z);
      return [x / len, y / len, z / len];
    });
  }, []);

  const icosahedronEdges = useMemo(() => [
    [0, 11], [0, 5], [0, 1], [0, 7], [0, 10],
    [1, 5], [1, 9], [1, 8], [1, 7],
    [2, 11], [2, 4], [2, 3], [2, 6], [2, 10],
    [3, 9], [3, 8], [3, 6], [3, 4],
    [4, 5], [4, 9], [4, 11],
    [5, 9], [5, 11],
    [6, 7], [6, 8], [6, 10],
    [7, 8], [7, 10],
    [8, 9],
    [10, 11]
  ], []);

  // Background Quantum Dust Particles
  const ambientParticles = useMemo(() => {
    const pts = [];
    for (let i = 0; i < 75; i++) {
      pts.push({
        x: (Math.random() - 0.5) * 650,
        y: (Math.random() - 0.5) * 450,
        z: (Math.random() - 0.5) * 650,
        size: Math.random() * 1.8 + 0.6,
        alpha: Math.random() * 0.5 + 0.2,
        speed: Math.random() * 0.4 + 0.1
      });
    }
    return pts;
  }, []);

  // Projected 2D screen positions for DOM HUD tags
  const [screenNodes, setScreenNodes] = useState([]);

  // Mouse / Touch Event Handlers for 3D Orbit
  const handlePointerDown = (e) => {
    isDraggingRef.current = true;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
    velRef.current = { x: 0, y: 0 };
  };

  const handlePointerMove = (e) => {
    if (!isDraggingRef.current) return;
    const dx = e.clientX - lastMousePosRef.current.x;
    const dy = e.clientY - lastMousePosRef.current.y;

    rotRef.current.y += dx * 0.007;
    rotRef.current.x = Math.max(-1.1, Math.min(1.1, rotRef.current.x + dy * 0.007));

    velRef.current = { x: dx * 0.007, y: dy * 0.007 };
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handlePointerUp = () => {
    isDraggingRef.current = false;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    targetZoomRef.current = Math.max(0.7, Math.min(1.6, targetZoomRef.current - e.deltaY * 0.001));
  };

  const resetCamera = () => {
    rotRef.current = { x: 0.35, y: 0.5, z: 0 };
    velRef.current = { x: 0, y: 0 };
    targetZoomRef.current = 1.0;
  };

  const focusAgent = (index) => {
    setSelectedAgent(index);
    const targetAngles = [0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2];
    rotRef.current.y = -targetAngles[index] + Math.PI / 4;
    rotRef.current.x = 0.25;
    targetZoomRef.current = 1.15;
  };

  // Main 3D Rendering Engine
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = (canvas.width = canvas.clientWidth * window.devicePixelRatio || 800);
    let height = (canvas.height = canvas.clientHeight * window.devicePixelRatio || 480);

    const handleResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth * (window.devicePixelRatio || 1);
      height = canvas.height = 420 * (window.devicePixelRatio || 1);
    };
    window.addEventListener('resize', handleResize);

    let frameCount = 0;
    let lastFpsUpdate = performance.now();
    let clock = 0;

    // 3D Vector Math Helpers
    const rotate3D = (p, rx, ry, rz) => {
      // Rotate Y
      const cosY = Math.cos(ry), sinY = Math.sin(ry);
      const x1 = p.x * cosY + p.z * sinY;
      const z1 = -p.x * sinY + p.z * cosY;

      // Rotate X
      const cosX = Math.cos(rx), sinX = Math.sin(rx);
      const y2 = p.y * cosX - z1 * sinX;
      const z2 = p.y * sinX + z1 * cosX;

      // Rotate Z
      const cosZ = Math.cos(rz), sinZ = Math.sin(rz);
      const x3 = x1 * cosZ - y2 * sinZ;
      const y3 = x1 * sinZ + y2 * cosZ;

      return { x: x3, y: y3, z: z2 };
    };

    const project3D = (p, cx, cy, fov = 420, zoom = 1.0) => {
      const scale = (fov * zoom) / (fov + p.z);
      return {
        x: cx + p.x * scale,
        y: cy + p.y * scale,
        scale,
        z: p.z
      };
    };

    // Render Loop
    const render = (time) => {
      animFrameIdRef.current = requestAnimationFrame(render);
      clock += 0.016;

      // FPS Measurement
      frameCount++;
      if (time - lastFpsUpdate >= 1000) {
        setFps(((frameCount * 1000) / (time - lastFpsUpdate)).toFixed(1));
        frameCount = 0;
        lastFpsUpdate = time;
      }

      // Smooth Momentum & Auto-Orbit
      if (!isDraggingRef.current) {
        if (autoOrbit) {
          rotRef.current.y += (isRunning ? 0.009 : 0.0035);
        }
        rotRef.current.y += velRef.current.x;
        rotRef.current.x = Math.max(-1.1, Math.min(1.1, rotRef.current.x + velRef.current.y));
        velRef.current.x *= 0.92;
        velRef.current.y *= 0.92;
      }

      // Smooth Zoom & Explode Lerp
      zoomRef.current += (targetZoomRef.current - zoomRef.current) * 0.1;
      const targetExploded = exploded ? 1 : 0;
      explodedFactorRef.current += (targetExploded - explodedFactorRef.current) * 0.08;
      const exp = explodedFactorRef.current;

      const dpr = window.devicePixelRatio || 1;
      const cx = width / 2;
      const cy = height / 2;

      ctx.clearRect(0, 0, width, height);

      // Deep Space Radial Background
      const bgGrad = ctx.createRadialGradient(cx, cy, 10, cx, cy, width * 0.65);
      bgGrad.addColorStop(0, '#041019');
      bgGrad.addColorStop(0.45, '#02070c');
      bgGrad.addColorStop(1, '#000000');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      const rx = rotRef.current.x;
      const ry = rotRef.current.y;
      const rz = rotRef.current.z;
      const zoom = zoomRef.current * dpr;

      // 1. Perspective Cybernetic Grid Floor
      const gridY = 160 + exp * 60;
      ctx.lineWidth = 1 * dpr;
      for (let gz = -320; gz <= 320; gz += 40) {
        const p1 = rotate3D({ x: -360, y: gridY, z: gz }, rx, ry, rz);
        const p2 = rotate3D({ x: 360, y: gridY, z: gz }, rx, ry, rz);
        if (p1.z > -380 && p2.z > -380) {
          const pr1 = project3D(p1, cx, cy, 420, zoom);
          const pr2 = project3D(p2, cx, cy, 420, zoom);
          const alpha = Math.max(0, 0.18 - Math.abs(gz) / 2200);
          ctx.strokeStyle = `rgba(0, 245, 243, ${alpha})`;
          ctx.beginPath();
          ctx.moveTo(pr1.x, pr1.y);
          ctx.lineTo(pr2.x, pr2.y);
          ctx.stroke();
        }
      }
      for (let gx = -360; gx <= 360; gx += 40) {
        const p1 = rotate3D({ x: gx, y: gridY, z: -320 }, rx, ry, rz);
        const p2 = rotate3D({ x: gx, y: gridY, z: 320 }, rx, ry, rz);
        if (p1.z > -380 && p2.z > -380) {
          const pr1 = project3D(p1, cx, cy, 420, zoom);
          const pr2 = project3D(p2, cx, cy, 420, zoom);
          const alpha = Math.max(0, 0.18 - Math.abs(gx) / 2200);
          ctx.strokeStyle = `rgba(0, 245, 243, ${alpha})`;
          ctx.beginPath();
          ctx.moveTo(pr1.x, pr1.y);
          ctx.lineTo(pr2.x, pr2.y);
          ctx.stroke();
        }
      }

      // 2. Ambient Floating Quantum Particles
      ambientParticles.forEach((pt) => {
        const p = rotate3D({ x: pt.x, y: pt.y + Math.sin(clock * pt.speed) * 12, z: pt.z }, rx, ry, rz);
        if (p.z > -380) {
          const pr = project3D(p, cx, cy, 420, zoom);
          ctx.fillStyle = `rgba(0, 245, 243, ${pt.alpha * Math.min(1, pr.scale)})`;
          ctx.beginPath();
          ctx.arc(pr.x, pr.y, pt.size * pr.scale * dpr, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      // 3. Exploded Architectural Planes (When Exploded View is Active)
      if (exp > 0.05) {
        const layers = [
          { y: 130 * exp, label: 'L-01 // CHROMA VECTOR STORAGE (all-MiniLM-L6-v2)', color: 'rgba(192, 132, 252, 0.4)' },
          { y: 40 * exp, label: 'L-02 // LANGGRAPH STATE MACHINE & ROUTER', color: 'rgba(0, 245, 243, 0.4)' },
          { y: -50 * exp, label: 'L-03 // SPECIALIST AGENT MULTI-THREAD PIPELINE', color: 'rgba(251, 191, 36, 0.4)' },
          { y: -130 * exp, label: 'L-04 // FACT GROUNDING & QUALITY VERIFICATION', color: 'rgba(52, 211, 153, 0.4)' }
        ];

        layers.forEach((layer) => {
          const rad = 140;
          ctx.lineWidth = 1 * dpr;
          ctx.strokeStyle = layer.color;
          ctx.setLineDash([4 * dpr, 6 * dpr]);
          ctx.beginPath();
          for (let a = 0; a <= Math.PI * 2; a += 0.2) {
            const px = Math.cos(a) * rad;
            const pz = Math.sin(a) * rad;
            const pt = rotate3D({ x: px, y: layer.y, z: pz }, rx, ry, rz);
            const pr = project3D(pt, cx, cy, 420, zoom);
            if (a === 0) ctx.moveTo(pr.x, pr.y);
            else ctx.lineTo(pr.x, pr.y);
          }
          ctx.closePath();
          ctx.stroke();
          ctx.setLineDash([]);

          // Layer Guide Line & Text Callout
          const tagPt = rotate3D({ x: rad + 15, y: layer.y, z: 0 }, rx, ry, rz);
          const tagPr = project3D(tagPt, cx, cy, 420, zoom);
          ctx.fillStyle = layer.color;
          ctx.font = `${Math.floor(9 * dpr * tagPr.scale)}px 'JetBrains Mono', monospace`;
          ctx.fillText(`+ ${layer.label}`, tagPr.x + 8 * dpr, tagPr.y + 3 * dpr);
        });
      }

      // 4. Concentric Gyroscopic Technical Orbital Rings
      const ringConfigs = [
        { radius: 105, tiltX: 0.35, tiltY: 0, speed: 0.6, color: '#00F5F3', dash: [3 * dpr, 3 * dpr], alpha: 0.5 },
        { radius: 145, tiltX: -0.4, tiltY: 0.3, speed: -0.45, color: '#c084fc', dash: [6 * dpr, 4 * dpr], alpha: 0.45 },
        { radius: 185, tiltX: 0.15, tiltY: -0.5, speed: 0.3, color: '#fbbf24', dash: [], alpha: 0.35 }
      ];

      ringConfigs.forEach((ring) => {
        const ringAngle = clock * ring.speed * (isRunning ? 2.2 : 1.0);
        ctx.strokeStyle = ring.color;
        ctx.lineWidth = 1.2 * dpr;
        if (ring.dash.length) ctx.setLineDash(ring.dash);
        else ctx.setLineDash([]);
        ctx.beginPath();

        for (let a = 0; a <= Math.PI * 2 + 0.1; a += 0.1) {
          const rawX = Math.cos(a + ringAngle) * ring.radius;
          const rawZ = Math.sin(a + ringAngle) * ring.radius;
          // Apply ring intrinsic tilt
          const tiltedY = rawX * Math.sin(ring.tiltX) + rawZ * Math.sin(ring.tiltY);
          const tiltedX = rawX * Math.cos(ring.tiltX);
          const tiltedZ = rawZ * Math.cos(ring.tiltY);

          const pt = rotate3D({ x: tiltedX, y: tiltedY, z: tiltedZ }, rx, ry, rz);
          const pr = project3D(pt, cx, cy, 420, zoom);
          if (a === 0) ctx.moveTo(pr.x, pr.y);
          else ctx.lineTo(pr.x, pr.y);
        }
        ctx.stroke();
        ctx.setLineDash([]);
      });

      // 5. Central Quantum Core (Rotating Geodesic Icosahedron Wireframe)
      const coreScale = 38 * (1.0 + Math.sin(clock * 2.5) * 0.05);
      const coreRotY = clock * 0.8;
      const coreRotX = clock * 0.4;

      // Project vertices
      const projectedCoreVerts = icosahedronVertices.map((v) => {
        // Rotate locally
        const cosY = Math.cos(coreRotY), sinY = Math.sin(coreRotY);
        const lx1 = v[0] * cosY + v[2] * sinY;
        const lz1 = -v[0] * sinY + v[2] * cosY;

        const cosX = Math.cos(coreRotX), sinX = Math.sin(coreRotX);
        const ly2 = v[1] * cosX - lz1 * sinX;
        const lz2 = v[1] * sinX + lz1 * cosX;

        // Rotate in world
        const wp = rotate3D({ x: lx1 * coreScale, y: ly2 * coreScale, z: lz2 * coreScale }, rx, ry, rz);
        return project3D(wp, cx, cy, 420, zoom);
      });

      // Draw Edges
      ctx.lineWidth = 1.2 * dpr;
      icosahedronEdges.forEach(([i1, i2]) => {
        const p1 = projectedCoreVerts[i1];
        const p2 = projectedCoreVerts[i2];
        const avgZ = (p1.z + p2.z) / 2;
        const alpha = Math.max(0.15, Math.min(0.9, 0.55 - avgZ / 400));
        ctx.strokeStyle = `rgba(0, 245, 243, ${alpha})`;
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      });

      // Draw Glowing Core Vertices
      projectedCoreVerts.forEach((pv) => {
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(pv.x, pv.y, 2.2 * pv.scale * dpr, 0, Math.PI * 2);
        ctx.fill();
      });

      // Core Inner Volumetric Flare
      const coreCenterPt = rotate3D({ x: 0, y: 0, z: 0 }, rx, ry, rz);
      const coreCenterPr = project3D(coreCenterPt, cx, cy, 420, zoom);
      const flareGrad = ctx.createRadialGradient(
        coreCenterPr.x, coreCenterPr.y, 2 * dpr,
        coreCenterPr.x, coreCenterPr.y, 50 * coreCenterPr.scale * dpr
      );
      flareGrad.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
      flareGrad.addColorStop(0.25, 'rgba(0, 245, 243, 0.7)');
      flareGrad.addColorStop(0.6, 'rgba(0, 245, 243, 0.15)');
      flareGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = flareGrad;
      ctx.beginPath();
      ctx.arc(coreCenterPr.x, coreCenterPr.y, 50 * coreCenterPr.scale * dpr, 0, Math.PI * 2);
      ctx.fill();

      // 6. Calculate 3D Agent Satellite Positions
      const orbitRad = 175 + exp * 45;
      const agent3DPositions = agents.map((agent, i) => {
        const baseAngle = (i * Math.PI) / 2;
        const orbitAngle = baseAngle + (autoOrbit && !isDraggingRef.current ? clock * 0.12 : 0);
        
        // Stagger Y in exploded view
        const explodedYOffsets = [-70, -20, 30, 80];
        const yPos = exp * explodedYOffsets[i] + Math.sin(clock * 1.5 + i) * 6;

        const rawPos = {
          x: Math.cos(orbitAngle) * orbitRad,
          y: yPos,
          z: Math.sin(orbitAngle) * orbitRad
        };

        const worldPos = rotate3D(rawPos, rx, ry, rz);
        const proj = project3D(worldPos, cx, cy, 420, zoom);

        return {
          agent,
          index: i,
          worldPos,
          proj,
          isActive: activeStage?.toLowerCase() === agent.id,
          isSelected: selectedAgent === i
        };
      });

      // 7. Render 3D Laser Conduits & Traveling Data Photons
      for (let i = 0; i < agent3DPositions.length; i++) {
        const curr = agent3DPositions[i];
        const next = agent3DPositions[(i + 1) % agent3DPositions.length];

        // Central Radial Bus Cable (Core to Node)
        ctx.strokeStyle = curr.agent.color;
        ctx.lineWidth = (curr.isActive ? 2.0 : 1.0) * dpr;
        ctx.setLineDash(curr.isActive ? [] : [4 * dpr, 4 * dpr]);
        ctx.globalAlpha = curr.isActive ? 0.85 : 0.3;
        ctx.beginPath();
        ctx.moveTo(coreCenterPr.x, coreCenterPr.y);
        ctx.lineTo(curr.proj.x, curr.proj.y);
        ctx.stroke();

        // Inter-Agent Workflow Arch (Curr -> Next)
        const midX = (curr.worldPos.x + next.worldPos.x) / 2;
        const midY = (curr.worldPos.y + next.worldPos.y) / 2 - 35; // Architectural arch lift
        const midZ = (curr.worldPos.z + next.worldPos.z) / 2;
        const midWorld = rotate3D({ x: midX, y: midY, z: midZ }, 0, 0, 0); // already in world space
        const midPr = project3D(midWorld, cx, cy, 420, zoom);

        ctx.strokeStyle = curr.agent.color;
        ctx.lineWidth = 1.4 * dpr;
        ctx.setLineDash([]);
        ctx.globalAlpha = curr.isActive ? 0.9 : 0.45;
        ctx.beginPath();
        ctx.moveTo(curr.proj.x, curr.proj.y);
        ctx.quadraticCurveTo(midPr.x, midPr.y, next.proj.x, next.proj.y);
        ctx.stroke();

        // Traveling Photon Pulses
        const pulseSpeed = isRunning ? 1.8 : 0.6;
        const t1 = ((clock * pulseSpeed + i * 0.25) % 1);
        const invT1 = 1 - t1;
        // Quadratic bezier interpolation: B(t) = (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
        const photonX = invT1 * invT1 * curr.proj.x + 2 * invT1 * t1 * midPr.x + t1 * t1 * next.proj.x;
        const photonY = invT1 * invT1 * curr.proj.y + 2 * invT1 * t1 * midPr.y + t1 * t1 * next.proj.y;

        ctx.globalAlpha = 1.0;
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = curr.agent.color;
        ctx.shadowBlur = 12 * dpr;
        ctx.beginPath();
        ctx.arc(photonX, photonY, 3.5 * dpr, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0; // reset
      }
      ctx.setLineDash([]);
      ctx.globalAlpha = 1.0;

      // 8. Fact-Checker Revision Feedback Loop Arc (Node 2 back to Node 0)
      const factNode = agent3DPositions[2];
      const resNode = agent3DPositions[0];
      if (factNode && resNode) {
        const loopMidWorld = rotate3D({ x: 0, y: -90 * exp - 45, z: 0 }, rx, ry, rz);
        const loopMidPr = project3D(loopMidWorld, cx, cy, 420, zoom);

        ctx.strokeStyle = '#fbbf24';
        ctx.lineWidth = 1 * dpr;
        ctx.setLineDash([2 * dpr, 4 * dpr]);
        ctx.globalAlpha = 0.4;
        ctx.beginPath();
        ctx.moveTo(factNode.proj.x, factNode.proj.y);
        ctx.quadraticCurveTo(loopMidPr.x, loopMidPr.y, resNode.proj.x, resNode.proj.y);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.globalAlpha = 1.0;
      }

      // 9. Render 3D Agent Beacons (Depth-Sorted)
      const sortedNodes = [...agent3DPositions].sort((a, b) => b.proj.z - a.proj.z);

      sortedNodes.forEach(({ agent, proj, isActive, isSelected }) => {
        const nodeRadius = (isSelected ? 22 : 18) * proj.scale * dpr;

        // Outer Aura Pulse
        const auraRadius = nodeRadius * (isActive ? 2.4 : 1.6) + Math.sin(clock * 4) * 3;
        const auraGrad = ctx.createRadialGradient(proj.x, proj.y, nodeRadius * 0.5, proj.x, proj.y, auraRadius);
        auraGrad.addColorStop(0, agent.color);
        auraGrad.addColorStop(0.5, agent.accentGlow);
        auraGrad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = auraGrad;
        ctx.beginPath();
        ctx.arc(proj.x, proj.y, auraRadius, 0, Math.PI * 2);
        ctx.fill();

        // 3D Metallic Pod Disc
        ctx.fillStyle = '#080d14';
        ctx.strokeStyle = agent.color;
        ctx.lineWidth = (isSelected ? 2.5 : 1.6) * dpr;
        ctx.beginPath();
        ctx.arc(proj.x, proj.y, nodeRadius, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Inner Glowing Micro-Core
        ctx.fillStyle = isActive ? '#ffffff' : agent.color;
        ctx.beginPath();
        ctx.arc(proj.x, proj.y, nodeRadius * 0.42, 0, Math.PI * 2);
        ctx.fill();

        // Orbiting Electron Dot
        const electronAngle = clock * 3.5;
        const elDist = nodeRadius * 1.35;
        const elX = proj.x + Math.cos(electronAngle) * elDist;
        const elY = proj.y + Math.sin(electronAngle) * elDist;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(elX, elY, 2 * dpr, 0, Math.PI * 2);
        ctx.fill();
      });

      // Update Screen Coordinates for Interactive HTML Badges
      const screenPosArray = agent3DPositions.map(({ agent, proj, index, isActive, isSelected }) => ({
        id: agent.id,
        index,
        x: proj.x / dpr,
        y: proj.y / dpr,
        scale: proj.scale,
        z: proj.z,
        color: agent.color,
        tag: agent.tag,
        name: agent.name,
        isActive,
        isSelected
      }));
      setScreenNodes(screenPosArray);
    };

    render(performance.now());

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animFrameIdRef.current) cancelAnimationFrame(animFrameIdRef.current);
    };
  }, [agents, ambientParticles, icosahedronEdges, icosahedronVertices, isRunning, activeStage, selectedAgent, autoOrbit, exploded]);

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      background: '#03070b',
      border: '1px solid rgba(0, 245, 243, 0.22)',
      borderRadius: 'var(--radius-sm)',
      padding: '1.25rem',
      marginBottom: '2.5rem',
      overflow: 'hidden',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.8), inset 0 0 40px rgba(0, 245, 243, 0.03)'
    }}>
      {/* 1. Cybernetic Header Status Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        paddingBottom: '0.85rem',
        marginBottom: '0.75rem',
        flexWrap: 'wrap',
        gap: '0.75rem',
      }}>
        {/* Left: Component Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: 'var(--color-accent)',
            boxShadow: '0 0 12px var(--color-accent)',
            animation: isRunning ? 'pulseCore 1s infinite' : 'none'
          }} />
          <div>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.78rem',
              fontWeight: 800,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: '#ffffff'
            }}>
              [ 3D ORCHESTRATION CORE // ARCHITECTURAL INSPECTOR ]
            </span>
            <span style={{
              marginLeft: '0.6rem',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.66rem',
              color: 'var(--text-muted)',
              letterSpacing: '0.08em'
            }}>
              ETHNOCARE CAD v3.2
            </span>
          </div>
        </div>

        {/* Right: Telemetry & Controls */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1.25rem',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.72rem',
          color: 'var(--text-muted)',
        }}>
          <div>
            CYCLE: <strong style={{ color: '#ffffff' }}>4-NODE DAG</strong>
          </div>
          <div>
            STATUS: <strong style={{ color: isRunning ? 'var(--color-accent)' : '#34d399' }}>
              {isRunning ? (activeStage?.toUpperCase() || 'SYNTHESIZING') : 'STANDBY // READY'}
            </strong>
          </div>
          <div>
            FPS: <strong style={{ color: '#00F5F3' }}>{fps}</strong>
          </div>
        </div>
      </div>

      {/* 2. Main 3D Viewport with HTML Layer Overlays */}
      <div
        ref={containerRef}
        onMouseDown={handlePointerDown}
        onMouseMove={handlePointerMove}
        onMouseUp={handlePointerUp}
        onMouseLeave={handlePointerUp}
        onWheel={handleWheel}
        style={{
          position: 'relative',
          width: '100%',
          height: '420px',
          cursor: isDraggingRef.current ? 'grabbing' : 'grab',
          userSelect: 'none',
          overflow: 'hidden',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid rgba(255, 255, 255, 0.06)'
        }}
      >
        {/* Hardware-Accelerated 3D Vector Canvas */}
        <canvas
          ref={canvasRef}
          style={{
            width: '100%',
            height: '100%',
            display: 'block'
          }}
        />

        {/* Technical Corner Brackets */}
        <div style={{ position: 'absolute', top: 10, left: 10, color: 'rgba(0, 245, 243, 0.4)', fontFamily: 'var(--font-mono)', fontSize: '0.65rem' }}>
          ┌─ [FOV: 420mm // ORBITAL MATRIX]
        </div>
        <div style={{ position: 'absolute', top: 10, right: 10, color: 'rgba(0, 245, 243, 0.4)', fontFamily: 'var(--font-mono)', fontSize: '0.65rem' }}>
          [ELEVATION: {(rotRef.current.x * 57.3).toFixed(1)}°] ─┐
        </div>
        <div style={{ position: 'absolute', bottom: 10, left: 10, color: 'rgba(0, 245, 243, 0.4)', fontFamily: 'var(--font-mono)', fontSize: '0.65rem' }}>
          └─ [CHROMA_DB // LANGGRAPH KERNEL]
        </div>
        <div style={{ position: 'absolute', bottom: 10, right: 10, color: 'rgba(0, 245, 243, 0.4)', fontFamily: 'var(--font-mono)', fontSize: '0.65rem' }}>
          [ZOOM: {(zoomRef.current).toFixed(2)}x] ─┘
        </div>

        {/* Dynamic 3D Projected Agent HUD Capsules */}
        {screenNodes.map((node) => {
          const isCurrentActive = activeStage?.toLowerCase() === node.id;
          return (
            <div
              key={node.id}
              onClick={(e) => {
                e.stopPropagation();
                focusAgent(node.index);
              }}
              style={{
                position: 'absolute',
                left: `${node.x}px`,
                top: `${node.y}px`,
                transform: 'translate(-50%, -150%)',
                zIndex: Math.floor(100 - node.z),
                pointerEvents: 'auto',
                cursor: 'pointer',
                transition: 'transform 0.15s ease-out',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.2rem'
              }}
            >
              {/* Floating Pill Badge */}
              <div style={{
                background: node.isSelected 
                  ? `rgba(0, 0, 0, 0.92)` 
                  : 'rgba(6, 11, 18, 0.85)',
                border: `1.5px solid ${node.color}`,
                boxShadow: node.isSelected || isCurrentActive 
                  ? `0 0 20px ${node.color}, inset 0 0 10px ${node.color}33` 
                  : `0 4px 12px rgba(0,0,0,0.7)`,
                padding: '0.25rem 0.6rem',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                backdropFilter: 'blur(8px)',
                whiteSpace: 'nowrap'
              }}>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.64rem',
                  fontWeight: 800,
                  color: node.color,
                  letterSpacing: '0.08em'
                }}>
                  [{node.tag}]
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  color: '#ffffff',
                  letterSpacing: '0.04em'
                }}>
                  {node.name.replace(' NODE', '').replace(' GATE', '').replace(' SYNTHESIZER', '')}
                </span>
                {isCurrentActive && (
                  <span style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: node.color,
                    boxShadow: `0 0 8px ${node.color}`
                  }} />
                )}
              </div>

              {/* Vertical Guide Ticker Line */}
              <div style={{
                width: '1px',
                height: '14px',
                background: `linear-gradient(to bottom, ${node.color}, transparent)`
              }} />
            </div>
          );
        })}
      </div>

      {/* 3. Interactive Toolbar & Exploded View Controls */}
      <div style={{
        marginTop: '0.85rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        paddingTop: '0.85rem',
      }}>
        {/* Agent Node Selector Buttons */}
        <div style={{ display: 'flex', gap: '0.45rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.68rem',
            color: 'var(--text-muted)',
            marginRight: '0.3rem'
          }}>
            FOCUS:
          </span>
          {agents.map((agent, i) => {
            const isSelected = selectedAgent === i;
            const Icon = agent.icon;
            return (
              <button
                key={agent.id}
                onClick={() => focusAgent(i)}
                style={{
                  background: isSelected ? `${agent.color}22` : 'rgba(255, 255, 255, 0.04)',
                  border: `1px solid ${isSelected ? agent.color : 'rgba(255, 255, 255, 0.12)'}`,
                  color: isSelected ? agent.color : 'var(--text-muted)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  padding: '0.35rem 0.65rem',
                  cursor: 'pointer',
                  borderRadius: '3px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  transition: 'all 0.15s cubic-bezier(0.165, 0.84, 0.44, 1)',
                  boxShadow: isSelected ? `0 0 12px ${agent.color}44` : 'none'
                }}
              >
                <Icon size={12} />
                <span>[{agent.tag}] {agent.name.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>

        {/* Viewport Control Toggles */}
        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => setAutoOrbit(!autoOrbit)}
            className="btn btn-secondary btn-sm"
            style={{
              fontSize: '0.7rem',
              fontFamily: 'var(--font-mono)',
              borderColor: autoOrbit ? 'var(--color-accent)' : 'rgba(255, 255, 255, 0.16)',
              color: autoOrbit ? 'var(--color-accent)' : 'var(--text-muted)'
            }}
          >
            <RefreshCw size={11} className={autoOrbit ? 'spin-slow' : ''} />
            <span>{autoOrbit ? 'AUTO-ORBIT: ON' : 'AUTO-ORBIT: OFF'}</span>
          </button>

          <button
            onClick={() => setExploded(!exploded)}
            className="btn btn-secondary btn-sm"
            style={{
              fontSize: '0.7rem',
              fontFamily: 'var(--font-mono)',
              borderColor: exploded ? 'var(--color-accent)' : 'rgba(255, 255, 255, 0.16)',
              color: exploded ? 'var(--color-accent)' : '#ffffff',
              background: exploded ? 'rgba(0, 245, 243, 0.12)' : 'transparent',
              boxShadow: exploded ? '0 0 14px rgba(0, 245, 243, 0.3)' : 'none'
            }}
          >
            <Layers size={11} />
            <span>{exploded ? 'ASSEMBLE CORE' : 'EXPLODED CAD VIEW'}</span>
          </button>

          <button
            onClick={resetCamera}
            className="btn btn-secondary btn-sm"
            style={{
              fontSize: '0.7rem',
              fontFamily: 'var(--font-mono)',
              borderColor: 'rgba(255, 255, 255, 0.16)',
              color: 'var(--text-muted)'
            }}
          >
            <Compass size={11} />
            <span>RESET CAM</span>
          </button>
        </div>
      </div>

      {/* 4. Active Node Deep Telemetry Card (Architectural Inspector Readout) */}
      <div style={{
        marginTop: '0.85rem',
        padding: '0.9rem 1.1rem',
        background: '#05090e',
        border: `1px solid ${agents[selectedAgent].color}44`,
        borderRadius: '3px',
        boxShadow: `0 4px 20px rgba(0,0,0,0.6), inset 0 0 20px ${agents[selectedAgent].color}11`
      }}>
        {/* Header line */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.72rem',
              fontWeight: 800,
              color: agents[selectedAgent].color,
              letterSpacing: '0.08em'
            }}>
              TELEMETRY INSPECTOR [{agents[selectedAgent].tag}] // {agents[selectedAgent].name}
            </span>
            <span style={{
              fontSize: '0.7rem',
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono)'
            }}>
              ({agents[selectedAgent].role})
            </span>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.9rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.68rem'
          }}>
            <div>LATENCY: <strong style={{ color: '#ffffff' }}>{agents[selectedAgent].latency}</strong></div>
            <div>VERIFIABILITY: <strong style={{ color: agents[selectedAgent].color }}>{agents[selectedAgent].precision}</strong></div>
          </div>
        </div>

        {/* Description & Technical Pipeline Grid */}
        <div style={{ fontSize: '0.82rem', color: '#d1d5db', lineHeight: 1.5, marginBottom: '0.6rem' }}>
          {agents[selectedAgent].desc}
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '0.6rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          paddingTop: '0.6rem',
          fontSize: '0.72rem',
          fontFamily: 'var(--font-mono)'
        }}>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>INTEGRATED ENGINES: </span>
            <strong style={{ color: '#ffffff' }}>{agents[selectedAgent].tools.join(' · ')}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>FAILOVER SAFEGUARD: </span>
            <strong style={{ color: '#34d399' }}>{agents[selectedAgent].failover}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>GRAPH STATE MUTATION: </span>
            <strong style={{ color: 'var(--color-accent)' }}>{agents[selectedAgent].stateTarget}</strong>
          </div>
        </div>

        <div style={{
          marginTop: '0.5rem',
          fontSize: '0.66rem',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-dim)',
          textAlign: 'right'
        }}>
          CLICK AND DRAG VIEWPORT TO ROTATE 360° · SCROLL TO ZOOM · SELECT AGENT TO FOCUS TELEMETRY
        </div>
      </div>
    </div>
  );
}

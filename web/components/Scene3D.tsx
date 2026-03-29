"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";

function FloatingGeometry() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.x = state.clock.elapsedTime * 0.15;
    meshRef.current.rotation.y = state.clock.elapsedTime * 0.2;
    meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.3;
  });

  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[2, 1]} />
      <meshStandardMaterial
        color="#4f6fff"
        emissive="#6366f1"
        emissiveIntensity={0.4}
        wireframe
        transparent
        opacity={0.7}
      />
    </mesh>
  );
}

function ParticleField({ count }: { count: number }) {
  const groupRef = useRef<THREE.Group>(null);

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 20;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 20;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return arr;
  }, [count]);

  useFrame((state) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y = state.clock.elapsedTime * 0.02;
    groupRef.current.rotation.x = state.clock.elapsedTime * 0.01;
  });

  return (
    <group ref={groupRef}>
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[positions, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          color="#8b9cf7"
          size={0.04}
          sizeAttenuation
          transparent
          opacity={0.6}
        />
      </points>
    </group>
  );
}

function GlowRing() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.z = -state.clock.elapsedTime * 0.1;
  });

  return (
    <mesh ref={meshRef} rotation={[Math.PI / 2, 0, 0]} position={[0, -1.2, 0]}>
      <torusGeometry args={[3, 0.02, 16, 100]} />
      <meshStandardMaterial
        color="#7c3aed"
        emissive="#7c3aed"
        emissiveIntensity={0.8}
        wireframe
        transparent
        opacity={0.5}
      />
    </mesh>
  );
}

export default function Scene3D() {
  const isMobile = typeof window !== "undefined" && window.innerWidth < 768;
  const particleCount = isMobile ? 300 : 800;

  return (
    <Canvas
      camera={{ position: [0, 0, 7], fov: 50 }}
      dpr={isMobile ? [1, 1.5] : [1, 2]}
      style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
      gl={{ alpha: true, antialias: true }}
    >
      <ambientLight intensity={0.15} />
      <pointLight position={[5, 5, 5]} color="#3b82f6" intensity={2} />
      <pointLight position={[-5, -3, 3]} color="#8b5cf6" intensity={1.5} />

      <FloatingGeometry />
      <ParticleField count={particleCount} />
      {!isMobile && <GlowRing />}

      <OrbitControls
        enableZoom={false}
        enablePan={false}
        autoRotate
        autoRotateSpeed={0.4}
        enableDamping
        maxPolarAngle={Math.PI / 1.8}
        minPolarAngle={Math.PI / 2.2}
      />
    </Canvas>
  );
}

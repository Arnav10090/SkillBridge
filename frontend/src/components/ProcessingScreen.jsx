import useAppStore from '../store/useAppStore'

const STAGES = [
    { min: 0, max: 25, label: 'Extracting text from documents', emoji: '📄', color: '#6366f1' },
    { min: 25, max: 50, label: 'Parsing skills with AI', emoji: '🤖', color: '#8b5cf6' },
    { min: 50, max: 65, label: 'Computing skill gaps', emoji: '📊', color: '#06b6d4' },
    { min: 65, max: 80, label: 'Generating learning pathway', emoji: '🗺️', color: '#10b981' },
    { min: 80, max: 95, label: 'Writing reasoning traces', emoji: '✍️', color: '#f59e0b' },
    { min: 95, max: 100, label: 'Finalizing your roadmap', emoji: '✅', color: '#10b981' },
]

export default function ProcessingScreen() {
    const { progress, statusMessage } = useAppStore()
    const currentIdx = STAGES.findIndex(s => progress >= s.min && progress < s.max)
    const activeStage = STAGES[currentIdx] || STAGES[STAGES.length - 1]

    return (
        <div className="mesh-bg" style={{
            minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            padding: 24, position: 'relative', overflow: 'hidden'
        }}>
            {/* Animated rings */}
            <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
                {[400, 500, 620].map((size, i) => (
                    <div key={size} style={{
                        position: 'absolute', width: size, height: size, borderRadius: '50%',
                        border: `1px solid rgba(99,102,241,${0.06 - i * 0.015})`,
                        animation: `spin-slow ${12 + i * 4}s linear infinite${i % 2 ? ' reverse' : ''}`,
                    }} />
                ))}
            </div>

            {/* Glow center */}
            <div style={{
                position: 'absolute', width: 300, height: 300, borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%)',
                filter: 'blur(40px)', pointerEvents: 'none'
            }} />

            <div style={{ maxWidth: 480, width: '100%', position: 'relative', zIndex: 1 }}>

                {/* Logo */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, marginBottom: 48 }}>
                    <div style={{
                        width: 40, height: 40, borderRadius: 12,
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20,
                        boxShadow: '0 0 24px rgba(99,102,241,0.5)'
                    }}>⚡</div>
                    <span style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 20, color: '#e2e8f0' }}>SkillBridge</span>
                </div>

                {/* Emoji + title */}
                <div style={{ textAlign: 'center', marginBottom: 40 }}>
                    <div style={{
                        fontSize: 56, marginBottom: 16,
                        filter: `drop-shadow(0 0 16px ${activeStage.color})`,
                        animation: 'float 2s ease-in-out infinite',
                        display: 'block'
                    }}>{activeStage.emoji}</div>
                    <h2 style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 24, color: '#e2e8f0', marginBottom: 8 }}>
                        Analyzing Your Profile
                    </h2>
                    <p style={{ color: 'rgba(148,163,184,0.7)', fontSize: 15 }}>
                        {statusMessage || activeStage.label + '...'}
                    </p>
                </div>

                {/* Progress bar */}
                <div style={{ marginBottom: 36 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                        <span style={{ fontSize: 13, color: 'rgba(148,163,184,0.6)' }}>Progress</span>
                        <span style={{ fontSize: 13, fontFamily: 'JetBrains Mono', color: '#a5b4fc', fontWeight: 500 }}>{progress}%</span>
                    </div>
                    <div style={{
                        height: 6, background: 'rgba(255,255,255,0.05)', borderRadius: 99, overflow: 'hidden',
                        border: '1px solid rgba(255,255,255,0.05)'
                    }}>
                        <div className="progress-shimmer" style={{
                            height: '100%', borderRadius: 99,
                            width: `${progress}%`, transition: 'width 0.7s ease-out',
                        }} />
                    </div>
                </div>

                {/* Stage list */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {STAGES.map((stage, i) => {
                        const done = progress >= stage.max
                        const current = progress >= stage.min && progress < stage.max
                        return (
                            <div key={i} style={{
                                display: 'flex', alignItems: 'center', gap: 12,
                                padding: '10px 16px', borderRadius: 12,
                                transition: 'all 0.4s ease',
                                background: current ? `rgba(${stage.color === '#6366f1' ? '99,102,241' : stage.color === '#8b5cf6' ? '139,92,246' : stage.color === '#06b6d4' ? '6,182,212' : stage.color === '#10b981' ? '16,185,129' : '245,158,11'},0.08)` : 'transparent',
                                border: current ? `1px solid ${stage.color}30` : '1px solid transparent',
                                opacity: done ? 0.45 : current ? 1 : 0.25,
                            }}>
                                <span style={{ fontSize: 18, minWidth: 24, textAlign: 'center' }}>{stage.emoji}</span>
                                <span style={{
                                    flex: 1, fontSize: 14,
                                    color: current ? '#e2e8f0' : 'rgba(148,163,184,0.7)',
                                    fontWeight: current ? 500 : 400
                                }}>{stage.label}</span>
                                {done && <span style={{ fontSize: 12, color: '#6ee7b7', fontFamily: 'JetBrains Mono' }}>done</span>}
                                {current && (
                                    <div style={{ display: 'flex', gap: 3 }}>
                                        {[0, 1, 2].map(j => (
                                            <div key={j} style={{
                                                width: 4, height: 4, borderRadius: '50%', background: stage.color,
                                                animation: `glow-pulse 1.2s ease-in-out infinite`,
                                                animationDelay: `${j * 0.2}s`
                                            }} />
                                        ))}
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}
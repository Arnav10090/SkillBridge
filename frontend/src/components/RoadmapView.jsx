import { useState, useCallback, useMemo, useEffect } from 'react'
import {
    ReactFlow, Background, Controls, MiniMap,
    useNodesState, useEdgesState, Handle, Position, MarkerType
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import useAppStore from '../store/useAppStore'

const GAP_STYLE = {
    missing: { border: '#ef4444', bg: 'rgba(239,68,68,0.06)', text: '#fca5a5', glow: '0 0 20px rgba(239,68,68,0.25)' },
    weak: { border: '#f59e0b', bg: 'rgba(245,158,11,0.06)', text: '#fcd34d', glow: '0 0 20px rgba(245,158,11,0.25)' },
    implied: { border: '#8b5cf6', bg: 'rgba(139,92,246,0.06)', text: '#c4b5fd', glow: '0 0 20px rgba(139,92,246,0.25)' },
    overqualified: { border: '#10b981', bg: 'rgba(16,185,129,0.06)', text: '#6ee7b7', glow: '0 0 20px rgba(16,185,129,0.15)' },
}
const CAT_COLOR = { technical: '#6366f1', soft: '#10b981', domain: '#f59e0b', tool: '#3b82f6' }

function SkillNode({ data, selected }) {
    const style = data.is_implied ? GAP_STYLE.implied : (GAP_STYLE[data.gap_type] || GAP_STYLE.missing)
    return (
        <>
            <Handle type="target" position={Position.Left} style={{ background: style.border, border: 'none', width: 8, height: 8 }} />
            <div onClick={() => data.onSelect(data)} style={{
                background: style.bg,
                border: `1.5px solid ${selected ? '#a5b4fc' : style.border}`,
                borderRadius: 14, padding: '12px 14px', minWidth: 180, maxWidth: 210,
                boxShadow: selected ? `0 0 0 2px #6366f1, ${style.glow}` : style.glow,
                cursor: 'pointer', transition: 'all 0.2s',
                backdropFilter: 'blur(10px)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span style={{ fontSize: 10, fontFamily: 'JetBrains Mono', fontWeight: 500, padding: '2px 6px', borderRadius: 20, color: style.text, background: `${style.border}22`, border: `1px solid ${style.border}33` }}>
                        Step {data.step_number}
                    </span>
                    {data.is_implied && <span style={{ fontSize: 9, color: '#c4b5fd', fontWeight: 600 }}>PREREQ</span>}
                </div>
                <div style={{ fontFamily: 'Syne', fontWeight: 700, color: '#e2e8f0', fontSize: 13, marginBottom: 8, lineHeight: 1.3 }}>
                    {data.skill_name}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <div style={{ width: 5, height: 5, borderRadius: '50%', background: CAT_COLOR[data.skill_category] || '#64748b' }} />
                        <span style={{ fontSize: 10, color: style.text, opacity: 0.7 }}>{data.skill_category}</span>
                    </div>
                    <span style={{ fontSize: 10, fontFamily: 'JetBrains Mono', color: style.text }}>{data.estimated_hours}h</span>
                </div>
                <div style={{ height: 3, background: 'rgba(255,255,255,0.06)', borderRadius: 99, overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${Math.round(data.coverage_score * 100)}%`, background: style.border, borderRadius: 99, transition: 'width 0.5s', boxShadow: `0 0 6px ${style.border}` }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 3 }}>
                    <span style={{ fontSize: 9, color: 'rgba(100,116,139,0.5)' }}>coverage</span>
                    <span style={{ fontSize: 9, fontFamily: 'JetBrains Mono', color: style.text, opacity: 0.6 }}>{Math.round(data.coverage_score * 100)}%</span>
                </div>
            </div>
            <Handle type="source" position={Position.Right} style={{ background: style.border, border: 'none', width: 8, height: 8 }} />
        </>
    )
}

const nodeTypes = { skillNode: SkillNode }

function buildGraph(pathway, onSelect) {
    if (!pathway?.length) return { nodes: [], edges: [] }
    const COLS = 3, XG = 280, YG = 160
    const nodes = pathway.map((step, i) => ({
        id: step.skill_id,
        type: 'skillNode',
        position: { x: (i % COLS) * XG + (Math.floor(i / COLS) % 2 === 1 ? 60 : 0), y: Math.floor(i / COLS) * YG },
        data: { ...step, onSelect, is_implied: step.is_implied_prereq }
    }))
    const edges = []
    for (let i = 0; i < pathway.length - 1; i++) {
        const curr = pathway[i], next = pathway[i + 1]
        edges.push({
            id: `e-${curr.skill_id}-${next.skill_id}`,
            source: curr.skill_id, target: next.skill_id,
            type: 'smoothstep', animated: curr.gap_type === 'missing',
            style: {
                stroke: next.is_implied_prereq ? '#8b5cf6'
                    : curr.gap_type === 'missing' ? '#ef4444'
                        : curr.gap_type === 'weak' ? '#f59e0b'
                            : 'rgba(255,255,255,0.08)',
                strokeWidth: 1.5,
                strokeDasharray: next.is_implied_prereq ? '5,3' : '4,3',
                opacity: 0.6
            },
            markerEnd: {
                type: MarkerType.ArrowClosed,
                color: next.is_implied_prereq ? '#8b5cf6'
                    : curr.gap_type === 'missing' ? '#ef4444'
                        : curr.gap_type === 'weak' ? '#f59e0b'
                            : 'rgba(255,255,255,0.12)'
            }
        })
    }
    return { nodes, edges }
}

function TraceDrawer({ step, onClose }) {
    if (!step) return null
    const style = step.is_implied_prereq ? GAP_STYLE.implied : (GAP_STYLE[step.gap_type] || GAP_STYLE.missing)
    return (
        <div style={{
            position: 'absolute', top: 0, right: 0, height: '100%', width: 380, zIndex: 30,
            background: 'rgba(5,5,8,0.97)', borderLeft: '1px solid rgba(255,255,255,0.06)',
            backdropFilter: 'blur(20px)', display: 'flex', flexDirection: 'column', overflow: 'hidden',
            animation: 'fadeIn 0.2s ease-out'
        }}>
            {/* Header */}
            <div style={{ padding: '20px', borderBottom: '1px solid rgba(255,255,255,0.06)', background: `${style.border}08` }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
                    <div>
                        <div style={{ display: 'flex', gap: 6, marginBottom: 8, flexWrap: 'wrap' }}>
                            <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 20, background: `${style.border}15`, border: `1px solid ${style.border}30`, color: style.text, fontWeight: 500 }}>
                                {step.is_implied_prereq ? 'implied prereq' : step.gap_type}
                            </span>
                            <span style={{ fontSize: 11, color: 'rgba(100,116,139,0.6)' }}>Step {step.step_number}</span>
                        </div>
                        <div style={{ fontFamily: 'Syne', fontWeight: 700, color: '#e2e8f0', fontSize: 16, lineHeight: 1.3 }}>{step.skill_name}</div>
                        <div style={{ fontSize: 12, color: 'rgba(100,116,139,0.6)', marginTop: 2, textTransform: 'capitalize' }}>{step.skill_category} skill</div>
                    </div>
                    <button onClick={onClose} style={{ width: 28, height: 28, borderRadius: 8, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)', color: 'rgba(148,163,184,0.7)', cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>×</button>
                </div>
            </div>

            {/* Content */}
            <div style={{ flex: 1, overflowY: 'auto', padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>

                {/* Metrics */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
                    {[['P-Score', step.p_score?.toFixed(3), '#6366f1'], ['Coverage', `${Math.round(step.coverage_score * 100)}%`, style.border], ['Difficulty', `${step.difficulty}/5`, '#f59e0b']].map(([l, v, c]) => (
                        <div key={l} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, padding: '10px', textAlign: 'center' }}>
                            <div style={{ fontFamily: 'JetBrains Mono', fontWeight: 600, fontSize: 15, color: c, marginBottom: 2 }}>{v}</div>
                            <div style={{ fontSize: 10, color: 'rgba(100,116,139,0.6)' }}>{l}</div>
                        </div>
                    ))}
                </div>

                {/* Coverage bar */}
                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                        <span style={{ color: 'rgba(148,163,184,0.6)' }}>Current Coverage</span>
                        <span style={{ fontFamily: 'JetBrains Mono', color: style.border }}>{Math.round(step.coverage_score * 100)}%</span>
                    </div>
                    <div style={{ height: 6, background: 'rgba(255,255,255,0.05)', borderRadius: 99, overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${Math.round(step.coverage_score * 100)}%`, background: style.border, borderRadius: 99, boxShadow: `0 0 8px ${style.border}` }} />
                    </div>
                </div>

                {/* Reasoning trace */}
                {step.reasoning_trace && (
                    <div style={{ padding: 14, borderRadius: 12, background: `${style.border}08`, border: `1px solid ${style.border}20` }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                            <span style={{ fontSize: 14 }}>⭐</span>
                            <span style={{ fontSize: 12, fontWeight: 600, color: 'rgba(226,232,240,0.9)' }}>Why This Is Recommended</span>
                        </div>
                        <p style={{ fontSize: 13, color: 'rgba(203,213,225,0.8)', lineHeight: 1.6, margin: 0 }}>{step.reasoning_trace}</p>
                    </div>
                )}

                {/* Modules */}
                {step.modules?.length > 0 && (
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                            <span style={{ fontSize: 14 }}>📚</span>
                            <span style={{ fontSize: 12, fontWeight: 600, color: 'rgba(226,232,240,0.9)' }}>Recommended Modules ({step.modules.length})</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                            {step.modules.map((mod, i) => (
                                <div key={i} style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, padding: 14, transition: 'all 0.2s' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8, marginBottom: 8 }}>
                                        <div style={{ fontFamily: 'Syne', fontWeight: 600, fontSize: 13, color: '#e2e8f0', lineHeight: 1.3 }}>{mod.title}</div>
                                        <a href={mod.url} target="_blank" rel="noopener noreferrer" style={{ width: 24, height: 24, borderRadius: 6, background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, color: '#818cf8', textDecoration: 'none', flexShrink: 0 }}>↗</a>
                                    </div>
                                    <div style={{ fontSize: 12, color: 'rgba(100,116,139,0.6)', lineHeight: 1.5, marginBottom: 10 }}>{mod.description}</div>
                                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                                        {[mod.provider, `${mod.duration_hours}h`, `${mod.difficulty}/5 diff`].map((tag, j) => (
                                            <span key={j} style={{ fontSize: 11, padding: '2px 8px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 6, color: 'rgba(100,116,139,0.7)' }}>{tag}</span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Time estimate */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'rgba(99,102,241,0.05)', border: '1px solid rgba(99,102,241,0.15)', borderRadius: 10, padding: '10px 14px' }}>
                    <span style={{ fontSize: 18 }}>⏱️</span>
                    <div>
                        <div style={{ fontFamily: 'Syne', fontWeight: 600, color: '#e2e8f0', fontSize: 14 }}>{step.estimated_hours}h estimated</div>
                        <div style={{ fontSize: 11, color: 'rgba(100,116,139,0.6)' }}>to reach required proficiency level</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default function RoadmapView() {
    const { results, setStep, reset } = useAppStore()
    const [selectedStep, setSelectedStep] = useState(null)
    const [filter, setFilter] = useState('all')
    const { pathway = [], summary } = results || {}

    const filtered = useMemo(() => {
        if (filter === 'all') return pathway
        if (filter === 'missing') return pathway.filter(s => s.gap_type === 'missing' && !s.is_implied_prereq)
        if (filter === 'weak') return pathway.filter(s => s.gap_type === 'weak' && !s.is_implied_prereq)
        if (filter === 'implied') return pathway.filter(s => s.is_implied_prereq)
        return pathway
    }, [pathway, filter])

    const handleSelect = useCallback(data => setSelectedStep(data), [])
    const { nodes: initNodes, edges: initEdges } = useMemo(() => buildGraph(filtered, handleSelect), [filtered, handleSelect])
    const [nodes, setNodes, onNodesChange] = useNodesState(initNodes)
    const [edges, setEdges, onEdgesChange] = useEdgesState(initEdges)
    useEffect(() => { setNodes(initNodes); setEdges(initEdges) }, [initNodes, initEdges])

    if (!results) return null

    const stats = [
        ['🔴', pathway.filter(s => s.gap_type === 'missing').length, 'Missing'],
        ['🟡', pathway.filter(s => s.gap_type === 'weak').length, 'Weak'],
        ['🟣', pathway.filter(s => s.is_implied_prereq).length, 'Auto-added'],
        ['📚', summary?.total_modules || 0, 'Modules'],
        ['⏱️', `${summary?.total_hours || 0}h`, 'Total'],
    ]

    return (
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#050508' }}>
            {/* Header */}
            <header style={{
                flexShrink: 0, padding: '12px 24px',
                background: 'rgba(5,5,8,0.9)', backdropFilter: 'blur(20px)',
                borderBottom: '1px solid rgba(255,255,255,0.06)',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', zIndex: 40
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{ width: 32, height: 32, borderRadius: 9, background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, boxShadow: '0 0 16px rgba(99,102,241,0.4)' }}>⚡</div>
                        <span style={{ fontFamily: 'Syne', fontWeight: 700, color: '#e2e8f0', fontSize: 16 }}>SkillBridge</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'rgba(148,163,184,0.6)' }}>
                        <button onClick={() => setStep('results')} style={{ background: 'transparent', border: 'none', color: 'rgba(99,102,241,0.8)', cursor: 'pointer', fontSize: 13, padding: 0 }}>← Results</button>
                        <span>›</span>
                        <span style={{ color: 'rgba(226,232,240,0.8)', fontWeight: 500 }}>Roadmap</span>
                    </div>
                    <div style={{ display: 'none', gap: 16 }} className="lg:flex">
                        {stats.map(([icon, val, label]) => (
                            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 12, color: 'rgba(148,163,184,0.6)' }}>
                                <span style={{ fontSize: 13 }}>{icon}</span>
                                <strong style={{ color: '#e2e8f0', fontFamily: 'JetBrains Mono' }}>{val}</strong>
                                <span>{label}</span>
                            </div>
                        ))}
                    </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ display: 'flex', gap: 2, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: 3 }}>
                        {[['all', 'All'], ['missing', 'Missing'], ['weak', 'Weak'], ['implied', 'Prereqs']].map(([v, l]) => (
                            <button key={v} onClick={() => { setFilter(v); setSelectedStep(null) }} style={{
                                fontSize: 12, padding: '5px 12px', borderRadius: 7, border: 'none', cursor: 'pointer',
                                background: filter === v ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : 'transparent',
                                color: filter === v ? 'white' : 'rgba(148,163,184,0.6)',
                                fontWeight: filter === v ? 600 : 400, transition: 'all 0.2s'
                            }}>{l}</button>
                        ))}
                    </div>
                    <button onClick={reset} style={{ fontSize: 12, padding: '6px 12px', borderRadius: 8, background: 'transparent', border: '1px solid rgba(255,255,255,0.06)', color: 'rgba(148,163,184,0.5)', cursor: 'pointer' }}>↩ New</button>
                </div>
            </header>

            {/* Canvas */}
            <div style={{ flex: 1, position: 'relative' }}>
                <ReactFlow
                    key={filter}
                    nodes={nodes} edges={edges}
                    onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}
                    nodeTypes={nodeTypes}
                    fitView fitViewOptions={{ padding: 0.2 }}
                    minZoom={0.2} maxZoom={2}
                    proOptions={{ hideAttribution: true }}
                >
                    <Background color="rgba(255,255,255,0.03)" gap={32} size={1} />
                    <Controls showInteractive={false} />
                    <MiniMap
                        nodeColor={n => (n.data?.is_implied ? GAP_STYLE.implied : GAP_STYLE[n.data?.gap_type] || GAP_STYLE.missing).border}
                        maskColor="rgba(5,5,8,0.88)"
                        style={{ background: 'rgba(5,5,8,0.9)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12 }}
                    />
                </ReactFlow>

                {/* Legend */}
                <div style={{ position: 'absolute', bottom: 16, left: 16, zIndex: 20, background: 'rgba(5,5,8,0.9)', border: '1px solid rgba(255,255,255,0.06)', backdropFilter: 'blur(10px)', borderRadius: 12, padding: '10px 14px', display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    {[['Missing', '#ef4444'], ['Weak', '#f59e0b'], ['Implied Prereq', '#8b5cf6'], ['Overqualified', '#10b981']].map(([l, c]) => (
                        <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                            <div style={{ width: 8, height: 8, borderRadius: '50%', background: c, boxShadow: `0 0 6px ${c}` }} />
                            <span style={{ fontSize: 11, color: 'rgba(148,163,184,0.7)' }}>{l}</span>
                        </div>
                    ))}
                </div>

                {/* Empty state */}
                {filtered.length === 0 && (
                    <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: 48, marginBottom: 12 }}>✅</div>
                            <div style={{ fontFamily: 'Syne', fontWeight: 600, color: 'rgba(226,232,240,0.8)', fontSize: 16 }}>No gaps in this category!</div>
                            <div style={{ fontSize: 13, color: 'rgba(100,116,139,0.6)', marginTop: 4 }}>Try a different filter</div>
                        </div>
                    </div>
                )}

                {/* Trace drawer */}
                {selectedStep && <TraceDrawer step={selectedStep} onClose={() => setSelectedStep(null)} />}
            </div>
        </div>
    )
}
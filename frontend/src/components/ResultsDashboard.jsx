import { useState } from 'react'
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import useAppStore from '../store/useAppStore'

const DOMAIN_LABELS = {
    software_engineering: 'Software Eng', web_development: 'Web Dev',
    machine_learning: 'ML / AI', data_science: 'Data Science',
    data_engineering: 'Data Eng', devops: 'DevOps', databases: 'Databases',
    cloud: 'Cloud', security: 'Security', management: 'Management',
    soft_skills: 'Soft Skills', finance: 'Finance', marketing: 'Marketing'
}

function StatCard({ icon, label, value, sub, accent }) {
    return (
        <div style={{
            background: 'rgba(255,255,255,0.02)', border: `1px solid ${accent}25`,
            borderRadius: 16, padding: '20px', position: 'relative', overflow: 'hidden'
        }}>
            <div style={{ position: 'absolute', top: -20, right: -20, width: 80, height: 80, borderRadius: '50%', background: `${accent}08`, filter: 'blur(20px)' }} />
            <div style={{ fontSize: 22, marginBottom: 12 }}>{icon}</div>
            <div style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 28, color: '#e2e8f0', marginBottom: 4 }}>{value}</div>
            <div style={{ fontSize: 13, color: 'rgba(148,163,184,0.7)' }}>{label}</div>
            {sub && <div style={{ fontSize: 11, color: 'rgba(100,116,139,0.6)', marginTop: 2 }}>{sub}</div>}
        </div>
    )
}

function ReadinessGauge({ score }) {
    const color = score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444'
    const label = score >= 70 ? 'Role Ready' : score >= 40 ? 'Developing' : 'High Gap'
    const r = 54, circ = 2 * Math.PI * r, dash = (score / 100) * circ
    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', padding: 20 }}>
            <div style={{ position: 'relative', width: 140, height: 140 }}>
                <svg width="140" height="140" style={{ transform: 'rotate(-90deg)' }} viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
                    <circle cx="60" cy="60" r={r} fill="none" stroke={color} strokeWidth="10"
                        strokeLinecap="round" strokeDasharray={`${dash} ${circ}`}
                        style={{ filter: `drop-shadow(0 0 8px ${color})`, transition: 'stroke-dasharray 1s ease-out' }} />
                </svg>
                <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    <span style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: 30, color: '#e2e8f0' }}>{Math.round(score)}</span>
                    <span style={{ fontSize: 11, color: 'rgba(148,163,184,0.5)' }}>/ 100</span>
                </div>
            </div>
            <div style={{ fontFamily: 'Syne', fontWeight: 600, fontSize: 14, color, marginTop: 8 }}>{label}</div>
            <div style={{ fontSize: 12, color: 'rgba(100,116,139,0.6)', marginTop: 2 }}>Readiness Score</div>
        </div>
    )
}

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    return (
        <div style={{ background: 'rgba(5,5,8,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, padding: '8px 12px', fontSize: 12, color: '#e2e8f0' }}>
            <div style={{ color: 'rgba(148,163,184,0.7)', marginBottom: 2 }}>{label}</div>
            <div style={{ color: '#a5b4fc', fontWeight: 600 }}>{payload[0].value} gaps</div>
        </div>
    )
}

export default function ResultsDashboard() {
    const { results, setStep, reset } = useAppStore()
    const [showAllResume, setShowAllResume] = useState(false)
    const [showAllGaps, setShowAllGaps] = useState(false)
    const [showAllJD, setShowAllJD] = useState(false)

    if (!results) return null
    const { summary, resume_skills, jd_skills, gap_report, pathway } = results

    const radarData = (() => {
        const ds = {}
        jd_skills.forEach(s => {
            const d = s.category || 'technical'
            if (!ds[d]) ds[d] = { total: 0, covered: 0 }
            ds[d].total++
            if (resume_skills.find(r => r.skill_id === s.skill_id)) ds[d].covered++
        })
        return Object.entries(ds).map(([d, v]) => ({
            subject: d.charAt(0).toUpperCase() + d.slice(1),
            score: v.total > 0 ? Math.round((v.covered / v.total) * 100) : 0,
            fullMark: 100
        }))
    })()

    const barData = Object.entries(summary?.domain_breakdown || {})
        .sort(([, a], [, b]) => b - a).slice(0, 7)
        .map(([d, c]) => ({ name: DOMAIN_LABELS[d] || d, gaps: c }))

    const BAR_COLORS = ['#6366f1', '#818cf8', '#8b5cf6', '#a78bfa', '#06b6d4', '#22d3ee', '#67e8f9']
    const allGaps = gap_report.filter(g => g.gap_type !== 'overqualified')
    const displayGaps = showAllGaps ? allGaps : allGaps.slice(0, 6)
    const displayResume = showAllResume ? resume_skills : resume_skills.slice(0, 8)

    const GAP_COLORS = { missing: { bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.25)', text: '#fca5a5', dot: '#ef4444' }, weak: { bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.25)', text: '#fcd34d', dot: '#f59e0b' } }

    return (
        <div className="mesh-bg" style={{ minHeight: '100vh', color: '#e2e8f0' }}>

            {/* Header */}
            <header style={{
                position: 'sticky', top: 0, zIndex: 40, padding: '14px 32px',
                background: 'rgba(5,5,8,0.85)', backdropFilter: 'blur(20px)',
                borderBottom: '1px solid rgba(255,255,255,0.06)',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ width: 32, height: 32, borderRadius: 9, background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, boxShadow: '0 0 16px rgba(99,102,241,0.4)' }}>⚡</div>
                    <span style={{ fontFamily: 'Syne', fontWeight: 700, color: '#e2e8f0', fontSize: 16 }}>SkillBridge</span>
                    <span style={{ color: 'rgba(100,116,139,0.6)', fontSize: 14 }}>/</span>
                    <span style={{ fontSize: 14, color: 'rgba(148,163,184,0.7)' }}>Analysis Results</span>
                </div>
                <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                    <button onClick={reset} style={{
                        display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'rgba(148,163,184,0.6)',
                        background: 'transparent', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 8, padding: '6px 12px', cursor: 'pointer',
                        transition: 'all 0.2s'
                    }}>↩ New Analysis</button>
                    <button onClick={() => setStep('roadmap')} style={{
                        display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, fontFamily: 'Syne', fontWeight: 600,
                        background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', color: 'white', border: 'none',
                        borderRadius: 10, padding: '8px 18px', cursor: 'pointer',
                        boxShadow: '0 0 24px rgba(99,102,241,0.3)', transition: 'all 0.2s'
                    }}>View Roadmap →</button>
                </div>
            </header>

            <div style={{ maxWidth: 1280, margin: '0 auto', padding: '32px 24px', display: 'flex', flexDirection: 'column', gap: 24 }} className="animate-fade-up">

                {/* Row 1: Stats */}
                <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr 1fr 1fr 1fr', gap: 16 }}>
                    <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16 }}>
                        <ReadinessGauge score={summary?.readiness_score || 0} />
                    </div>
                    <StatCard icon="🔴" label="Missing Skills" value={summary?.missing_skills || 0} accent="#ef4444" />
                    <StatCard icon="🟡" label="Weak Skills" value={summary?.weak_skills || 0} accent="#f59e0b" />
                    <StatCard icon="📚" label="Modules Assigned" value={summary?.total_modules || 0} accent="#6366f1" />
                    <StatCard icon="⏱️" label="Estimated Hours" value={`${summary?.total_hours || 0}h`} accent="#10b981" />
                </div>

                {/* Row 2: Charts */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    {/* Radar */}
                    <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, padding: 24 }}>
                        <div style={{ fontFamily: 'Syne', fontWeight: 600, fontSize: 15, color: '#e2e8f0', marginBottom: 4 }}>Skill Coverage by Category</div>
                        <div style={{ fontSize: 12, color: 'rgba(100,116,139,0.7)', marginBottom: 16 }}>How well your resume covers each domain</div>
                        <ResponsiveContainer width="100%" height={240}>
                            <RadarChart data={radarData}>
                                <PolarGrid stroke="rgba(255,255,255,0.06)" />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(100,116,139,0.8)', fontSize: 11, fontFamily: 'DM Sans' }} />
                                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'rgba(100,116,139,0.5)', fontSize: 9 }} />
                                <Radar name="Coverage" dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} strokeWidth={2} dot={{ fill: '#6366f1', r: 3 }} />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Bar chart */}
                    <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, padding: 24 }}>
                        <div style={{ fontFamily: 'Syne', fontWeight: 600, fontSize: 15, color: '#e2e8f0', marginBottom: 4 }}>Gaps by Domain</div>
                        <div style={{ fontSize: 12, color: 'rgba(100,116,139,0.7)', marginBottom: 16 }}>Number of skill gaps per knowledge domain</div>
                        <ResponsiveContainer width="100%" height={240}>
                            <BarChart data={barData} layout="vertical" margin={{ left: 8, right: 16 }}>
                                <XAxis type="number" tick={{ fill: 'rgba(100,116,139,0.6)', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis type="category" dataKey="name" width={88} tick={{ fill: 'rgba(148,163,184,0.7)', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                                <Bar dataKey="gaps" radius={[0, 6, 6, 0]}>
                                    {barData.map((_, i) => <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />)}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Row 3: Skills Comparison */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
                    {/* Resume Skills */}
                    <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, padding: 20 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                            <div>
                                <div style={{ fontFamily: 'Syne', fontWeight: 600, color: '#e2e8f0', fontSize: 14 }}>Your Skills</div>
                                <div style={{ fontSize: 12, color: 'rgba(100,116,139,0.6)', marginTop: 2 }}>{resume_skills.length} detected from resume</div>
                            </div>
                            <span style={{ fontSize: 20 }}>✅</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                            {displayResume.map((s, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)', borderRadius: 8 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <div style={{ width: 6, height: 6, borderRadius: '50%', background: s.category === 'technical' ? '#6366f1' : s.category === 'soft' ? '#10b981' : '#f59e0b' }} />
                                        <span style={{ fontSize: 13, color: '#e2e8f0' }}>{s.name}</span>
                                    </div>
                                    <span style={{ fontSize: 11, color: s.level === 'expert' ? '#c084fc' : s.level === 'intermediate' ? '#818cf8' : 'rgba(100,116,139,0.7)', fontFamily: 'JetBrains Mono' }}>{s.level}</span>
                                </div>
                            ))}
                        </div>
                        {resume_skills.length > 8 && (
                            <button onClick={() => setShowAllResume(!showAllResume)} style={{ marginTop: 8, width: '100%', padding: '6px', background: 'transparent', border: 'none', color: 'rgba(99,102,241,0.7)', fontSize: 12, cursor: 'pointer' }}>
                                {showAllResume ? '↑ Show less' : `+ ${resume_skills.length - 8} more skills`}
                            </button>
                        )}
                    </div>

                    {/* JD Requirements */}
                    <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(99,102,241,0.12)', borderRadius: 16, padding: 20 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                            <div>
                                <div style={{ fontFamily: 'Syne', fontWeight: 600, color: '#e2e8f0', fontSize: 14 }}>Role Requirements</div>
                                <div style={{ fontSize: 12, color: 'rgba(100,116,139,0.6)', marginTop: 2 }}>{jd_skills.length} extracted from JD</div>
                            </div>
                            <span style={{ fontSize: 20 }}>🎯</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                            {(showAllJD ? jd_skills : jd_skills.slice(0, 8)).map((s, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(99,102,241,0.04)', border: '1px solid rgba(99,102,241,0.1)', borderRadius: 8 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#818cf8' }} />
                                        <span style={{ fontSize: 13, color: '#e2e8f0' }}>{s.name}</span>
                                    </div>
                                    <span style={{ fontSize: 11, color: s.requirement_type === 'required' ? '#f87171' : 'rgba(100,116,139,0.6)', fontFamily: 'JetBrains Mono' }}>
                                        {s.requirement_type === 'required' ? 'req' : 'pref'}
                                    </span>
                                </div>
                            ))}
                            {jd_skills.length > 8 && (
                                <button onClick={() => setShowAllJD(!showAllJD)} style={{ marginTop: 8, width: '100%', padding: '6px', background: 'transparent', border: 'none', color: 'rgba(99,102,241,0.7)', fontSize: 12, cursor: 'pointer' }}>
                                    {showAllJD ? '↑ Show less' : `+ ${jd_skills.length - 8} more requirements`}
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Gaps */}
                    <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(245,158,11,0.15)', borderRadius: 16, padding: 20 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                            <div>
                                <div style={{ fontFamily: 'Syne', fontWeight: 600, color: '#e2e8f0', fontSize: 14 }}>Identified Gaps</div>
                                <div style={{ fontSize: 12, color: 'rgba(100,116,139,0.6)', marginTop: 2 }}>{allGaps.length} skills need attention</div>
                            </div>
                            <span style={{ fontSize: 20 }}>⚠️</span>
                        </div>
                        <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
                            {['missing', 'weak'].map(t => {
                                const count = gap_report.filter(g => g.gap_type === t).length
                                const c = GAP_COLORS[t]
                                return (
                                    <div key={t} style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '3px 8px', background: c.bg, border: `1px solid ${c.border}`, borderRadius: 6 }}>
                                        <div style={{ width: 5, height: 5, borderRadius: '50%', background: c.dot }} />
                                        <span style={{ fontSize: 11, color: c.text }}>{t} ({count})</span>
                                    </div>
                                )
                            })}
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                            {displayGaps.map((g, i) => {
                                const c = GAP_COLORS[g.gap_type] || GAP_COLORS.missing
                                return (
                                    <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '7px 10px', background: c.bg, border: `1px solid ${c.border}`, borderRadius: 8 }}>
                                        <div>
                                            <div style={{ fontSize: 13, fontWeight: 500, color: c.text }}>{g.skill_name}</div>
                                            {g.closest_match && <div style={{ fontSize: 10, color: 'rgba(100,116,139,0.5)' }}>≈ {g.closest_match}</div>}
                                        </div>
                                        <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: c.text }}>{Math.round(g.coverage_score * 100)}%</span>
                                    </div>
                                )
                            })}
                        </div>
                        {allGaps.length > 6 && (
                            <button onClick={() => setShowAllGaps(!showAllGaps)} style={{ marginTop: 8, width: '100%', padding: '6px', background: 'transparent', border: 'none', color: 'rgba(245,158,11,0.7)', fontSize: 12, cursor: 'pointer' }}>
                                {showAllGaps ? '↑ Show less' : `+ ${allGaps.length - 6} more gaps`}
                            </button>
                        )}
                    </div>
                </div>

                {/* Row 4: Pathway Preview */}
                <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, padding: 24 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                        <div>
                            <div style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 16, color: '#e2e8f0' }}>Learning Pathway Preview</div>
                            <div style={{ fontSize: 12, color: 'rgba(100,116,139,0.6)', marginTop: 2 }}>First 5 steps · ordered by WGT priority score</div>
                        </div>
                        <button onClick={() => setStep('roadmap')} style={{
                            fontSize: 12, color: '#a5b4fc', background: 'rgba(99,102,241,0.08)',
                            border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, padding: '6px 12px', cursor: 'pointer'
                        }}>Full Roadmap →</button>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                        {pathway.slice(0, 5).map((step, i) => {
                            const gc = { missing: '#ef4444', weak: '#f59e0b', overqualified: '#10b981' }
                            const gc2 = { missing: 'rgba(239,68,68,0.08)', weak: 'rgba(245,158,11,0.08)', overqualified: 'rgba(16,185,129,0.08)' }
                            return (
                                <div key={i} style={{
                                    display: 'flex', alignItems: 'center', gap: 16, padding: '14px 16px',
                                    background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)',
                                    borderRadius: 12, transition: 'all 0.2s'
                                }}>
                                    <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Syne', fontWeight: 700, fontSize: 14, color: '#818cf8', flexShrink: 0 }}>
                                        {step.step_number}
                                    </div>
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
                                            <span style={{ fontFamily: 'Syne', fontWeight: 600, fontSize: 14, color: '#e2e8f0' }}>{step.skill_name}</span>
                                            <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 20, background: gc2[step.gap_type], border: `1px solid ${gc[step.gap_type] || '#6366f1'}30`, color: gc[step.gap_type] || '#818cf8', fontWeight: 500 }}>
                                                {step.gap_type}
                                            </span>
                                            {step.is_implied_prereq && <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 20, background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)', color: '#c4b5fd' }}>auto prereq</span>}
                                        </div>
                                        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                                            {step.modules?.slice(0, 2).map((m, j) => (
                                                <span key={j} style={{ fontSize: 11, color: 'rgba(100,116,139,0.6)', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 6, padding: '2px 8px' }}>📚 {m.title.slice(0, 30)}{m.title.length > 30 ? '...' : ''}</span>
                                            ))}
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                                        <div style={{ fontSize: 13, fontFamily: 'JetBrains Mono', color: '#818cf8', fontWeight: 600 }}>{step.estimated_hours}h</div>
                                        <div style={{ fontSize: 10, color: 'rgba(100,116,139,0.5)', marginTop: 2 }}>P:{step.p_score?.toFixed(2)}</div>
                                    </div>
                                </div>
                            )
                        })}
                    </div>

                    <button onClick={() => setStep('roadmap')} style={{
                        marginTop: 16, width: '100%', padding: '14px', borderRadius: 12, border: 'none', cursor: 'pointer',
                        background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', color: 'white',
                        fontFamily: 'Syne', fontWeight: 700, fontSize: 14,
                        boxShadow: '0 0 30px rgba(99,102,241,0.25)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                        transition: 'all 0.2s'
                    }}>
                        View Full Interactive Roadmap →
                    </button>
                </div>
            </div>
        </div>
    )
}
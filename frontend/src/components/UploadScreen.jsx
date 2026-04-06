import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { analyzeDocuments, pollStatus, getResults } from '../api/client'
import useAppStore from '../store/useAppStore'

function FloatingOrb({ style }) {
    return (
        <div className="absolute rounded-full pointer-events-none" style={{
            background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)',
            filter: 'blur(40px)',
            ...style
        }} />
    )
}

function DropZone({ label, sublabel, icon, file, onDrop, color }) {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop: useCallback(files => files[0] && onDrop(files[0]), [onDrop]),
        accept: {
            'application/pdf': [],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [],
            'text/plain': []
        },
        maxFiles: 1,
        maxSize: 5 * 1024 * 1024
    })

    const colors = {
        indigo: { ring: 'rgba(99,102,241,0.5)', glow: 'rgba(99,102,241,0.12)', text: '#a5b4fc' },
        violet: { ring: 'rgba(139,92,246,0.5)', glow: 'rgba(139,92,246,0.12)', text: '#c4b5fd' },
    }
    const c = colors[color]

    return (
        <div
            {...getRootProps()}
            style={{
                background: isDragActive
                    ? `rgba(${color === 'indigo' ? '99,102,241' : '139,92,246'},0.08)`
                    : file ? 'rgba(16,185,129,0.05)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${isDragActive ? c.ring : file ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.07)'}`,
                borderRadius: 24,
                padding: '44px 24px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden',
                boxShadow: isDragActive ? `0 0 40px ${c.glow}, inset 0 0 40px ${c.glow}` : 'none',
            }}
        >
            <input {...getInputProps()} />
            {!file && <>
                <div style={{ position: 'absolute', top: 0, left: 0, width: 24, height: 24, borderTop: `2px solid ${c.ring}`, borderLeft: `2px solid ${c.ring}`, borderRadius: '14px 0 0 0' }} />
                <div style={{ position: 'absolute', top: 0, right: 0, width: 24, height: 24, borderTop: `2px solid ${c.ring}`, borderRight: `2px solid ${c.ring}`, borderRadius: '0 14px 0 0' }} />
                <div style={{ position: 'absolute', bottom: 0, left: 0, width: 24, height: 24, borderBottom: `2px solid ${c.ring}`, borderLeft: `2px solid ${c.ring}`, borderRadius: '0 0 0 14px' }} />
                <div style={{ position: 'absolute', bottom: 0, right: 0, width: 24, height: 24, borderBottom: `2px solid ${c.ring}`, borderRight: `2px solid ${c.ring}`, borderRadius: '0 0 14px 0' }} />
            </>}

            <div style={{ textAlign: 'center' }}>
                {file ? (
                    <>
                        <div style={{
                            width: 72, height: 72, borderRadius: 20,
                            background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            margin: '0 auto 16px', fontSize: 32
                        }}>✓</div>
                        <div style={{ color: '#6ee7b7', fontFamily: 'Syne', fontWeight: 700, fontSize: 16, marginBottom: 6 }}>
                            {file.name.length > 22 ? file.name.slice(0, 19) + '...' : file.name}
                        </div>
                        <div style={{ color: 'rgba(100,116,139,0.8)', fontSize: 13 }}>
                            {(file.size / 1024).toFixed(1)} KB · Click to change
                        </div>
                    </>
                ) : (
                    <>
                        <div style={{
                            width: 72, height: 72, borderRadius: 20,
                            background: `rgba(${color === 'indigo' ? '99,102,241' : '139,92,246'},0.1)`,
                            border: `1px solid ${c.ring}`,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            margin: '0 auto 18px', fontSize: 34,
                            boxShadow: `0 0 28px ${c.glow}`
                        }}>{icon}</div>
                        <div style={{ fontFamily: 'Syne', fontWeight: 700, color: '#e2e8f0', fontSize: 18, marginBottom: 8 }}>{label}</div>
                        <div style={{ color: 'rgba(148,163,184,0.65)', fontSize: 14, marginBottom: 14 }}>{sublabel}</div>
                        <div style={{
                            display: 'inline-flex', alignItems: 'center', gap: 6,
                            background: `rgba(${color === 'indigo' ? '99,102,241' : '139,92,246'},0.08)`,
                            border: `1px solid rgba(${color === 'indigo' ? '99,102,241' : '139,92,246'},0.2)`,
                            borderRadius: 8, padding: '6px 14px',
                            color: c.text, fontSize: 13, fontWeight: 500
                        }}>
                            {isDragActive ? '📂 Drop it here' : 'PDF · DOCX · TXT · Max 5MB'}
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}

export default function UploadScreen() {
    const [resumeFile, setResumeFile] = useState(null)
    const [jdFile, setJdFile] = useState(null)
    const [loading, setLoading] = useState(false)
    const { setStep, setJobId, setProgress, setResults, setError } = useAppStore()

    const handleAnalyze = async () => {
        if (!resumeFile || !jdFile) return
        setLoading(true)
        setStep('processing')
        try {
            const { job_id } = await analyzeDocuments(resumeFile, jdFile)
            setJobId(job_id)
            let attempts = 0
            while (attempts < 240) {
                await new Promise(r => setTimeout(r, 2000))
                const status = await pollStatus(job_id)
                setProgress(status.progress, status.message)
                if (status.status === 'complete') { setResults(await getResults(job_id)); return }
                if (status.status === 'failed') throw new Error(status.message || 'Analysis failed')
                attempts++
            }
            throw new Error('Analysis timed out. Please try again.')
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Something went wrong')
            setLoading(false)
        }
    }

    const canAnalyze = resumeFile && jdFile && !loading

    return (
        <div className="mesh-bg grid-bg" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <FloatingOrb style={{ width: 500, height: 500, top: -150, left: -150 }} />
            <FloatingOrb style={{ width: 350, height: 350, bottom: -80, right: -80, background: 'radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%)' }} />

            {/* Header */}
            <header style={{
                padding: '20px 40px',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
                background: 'rgba(5,5,8,0.6)',
                backdropFilter: 'blur(20px)',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                position: 'sticky', top: 0, zIndex: 50
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                        width: 36, height: 36, borderRadius: 10,
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 18, boxShadow: '0 0 20px rgba(99,102,241,0.4)'
                    }}>⚡</div>
                    <span style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 18, color: '#e2e8f0' }}>SkillBridge</span>
                </div>
                <div style={{
                    fontSize: 12, color: 'rgba(165,180,252,0.7)',
                    background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)',
                    borderRadius: 20, padding: '4px 14px', fontFamily: 'JetBrains Mono', fontWeight: 500
                }}>
                    AI-Adaptive Onboarding Engine
                </div>
            </header>

            {/* Main — 50/50 split */}
            <main style={{ flex: 1, display: 'flex', alignItems: 'stretch' }}>

                {/* ── LEFT: Hero — centered ─────────────────────────────── */}
                <div style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textAlign: 'center',
                    padding: '60px 52px',
                    borderRight: '1px solid rgba(255,255,255,0.05)',
                }}>
                    {/* Badge */}
                    <div style={{
                        display: 'inline-flex', alignItems: 'center', gap: 8,
                        background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)',
                        borderRadius: 24, padding: '6px 16px', marginBottom: 32
                    }}>
                        <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#6366f1', boxShadow: '0 0 8px #6366f1', animation: 'glow-pulse 2s ease-in-out infinite' }} />
                        <span style={{ fontSize: 12, color: '#a5b4fc', fontWeight: 500 }}>Powered by AI · Zero Hallucinations · WGT Algorithm</span>
                    </div>

                    {/* Heading */}
                    <h1 style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: 'clamp(38px,4vw,60px)', lineHeight: 1.08, marginBottom: 24 }}>
                        Your<br />
                        Personalized<br />
                        <span className="gradient-text">Learning Path</span><br />
                        <span style={{ color: 'rgba(226,232,240,0.85)' }}>Starts Here</span>
                    </h1>

                    {/* Description */}
                    <p style={{ color: 'rgba(148,163,184,0.75)', fontSize: 16, lineHeight: 1.8, maxWidth: 400, marginBottom: 48 }}>
                        Upload your resume and a job description. Our AI analyzes skill gaps
                        and generates a prioritized roadmap in under 100 seconds.
                    </p>

                    {/* Feature pills — 2x2 centered grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, width: '100%', maxWidth: 420 }}>
                        {[
                            ['⚡', 'Under 100 seconds', 'Fast async pipeline'],
                            ['🎯', 'Zero hallucinations', 'Closed catalog'],
                            ['🔍', 'Full reasoning traces', 'Every step explained'],
                            ['📊', 'WGT algorithm', 'Original priority scoring'],
                        ].map(([icon, title, desc]) => (
                            <div key={title} style={{
                                display: 'flex', alignItems: 'center', gap: 10,
                                background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                                borderRadius: 12, padding: '12px 14px', textAlign: 'left',
                            }}>
                                <span style={{ fontSize: 20, flexShrink: 0 }}>{icon}</span>
                                <div>
                                    <div style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0', fontFamily: 'Syne' }}>{title}</div>
                                    <div style={{ fontSize: 11, color: 'rgba(148,163,184,0.6)', marginTop: 2 }}>{desc}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* ── RIGHT: Upload zones — larger ─────────────────────── */}
                <div style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '60px 52px',
                }}>
                    <div style={{ width: '100%', maxWidth: 560 }}>

                        {/* Drop zones */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
                            <div>
                                <div style={{ fontSize: 13, fontWeight: 600, color: 'rgba(165,180,252,0.7)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12, paddingLeft: 4 }}>
                                    01 · Your Resume
                                </div>
                                <DropZone label="Upload Resume" sublabel="Your work history & skills" icon="📄" file={resumeFile} onDrop={setResumeFile} color="indigo" />
                            </div>
                            <div>
                                <div style={{ fontSize: 13, fontWeight: 600, color: 'rgba(196,181,253,0.7)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12, paddingLeft: 4 }}>
                                    02 · Job Description
                                </div>
                                <DropZone label="Upload Job Description" sublabel="Target role requirements" icon="💼" file={jdFile} onDrop={setJdFile} color="violet" />
                            </div>
                        </div>

                        {/* CTA */}
                        <button
                            onClick={handleAnalyze}
                            disabled={!canAnalyze}
                            style={{
                                width: '100%', padding: '20px 32px', borderRadius: 18,
                                border: 'none', cursor: canAnalyze ? 'pointer' : 'not-allowed',
                                fontSize: 18, fontFamily: 'Syne', fontWeight: 700, letterSpacing: '0.02em',
                                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
                                transition: 'all 0.3s ease',
                                background: canAnalyze
                                    ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%)'
                                    : 'rgba(255,255,255,0.05)',
                                color: canAnalyze ? 'white' : 'rgba(148,163,184,0.4)',
                                boxShadow: canAnalyze ? '0 0 40px rgba(99,102,241,0.35), 0 8px 32px rgba(99,102,241,0.2)' : 'none',
                            }}
                            onMouseEnter={e => { if (canAnalyze) { e.target.style.transform = 'translateY(-2px)'; e.target.style.boxShadow = '0 0 60px rgba(99,102,241,0.5), 0 12px 40px rgba(99,102,241,0.3)' } }}
                            onMouseLeave={e => { if (canAnalyze) { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 0 40px rgba(99,102,241,0.35), 0 8px 32px rgba(99,102,241,0.2)' } }}
                        >
                            ⚡ Analyze My Skill Gap →
                        </button>

                        {/* Status hint */}
                        <p style={{ textAlign: 'center', marginTop: 16, fontSize: 14, color: 'rgba(148,163,184,0.45)' }}>
                            {!resumeFile && !jdFile && 'Upload both files to get started'}
                            {resumeFile && !jdFile && 'Now upload the job description →'}
                            {!resumeFile && jdFile && 'Now upload your resume →'}
                            {resumeFile && jdFile && '✓ Ready — click Analyze to begin'}
                        </p>
                    </div>
                </div>

            </main>
        </div>
    )
}
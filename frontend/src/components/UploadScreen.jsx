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
        indigo: { ring: 'rgba(99,102,241,0.5)', glow: 'rgba(99,102,241,0.1)', dot: '#6366f1', text: '#a5b4fc' },
        violet: { ring: 'rgba(139,92,246,0.5)', glow: 'rgba(139,92,246,0.1)', dot: '#8b5cf6', text: '#c4b5fd' },
    }
    const c = colors[color]

    return (
        <div
            {...getRootProps()}
            style={{
                background: isDragActive ? `rgba(${color === 'indigo' ? '99,102,241' : '139,92,246'},0.08)` :
                    file ? 'rgba(16,185,129,0.05)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${isDragActive ? c.ring : file ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.07)'}`,
                borderRadius: 20,
                padding: '32px 24px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden',
                boxShadow: isDragActive ? `0 0 40px ${c.glow}, inset 0 0 40px ${c.glow}` : 'none',
            }}
        >
            <input {...getInputProps()} />

            {/* Corner accents */}
            {!file && <>
                <div style={{ position: 'absolute', top: 0, left: 0, width: 20, height: 20, borderTop: `2px solid ${c.ring}`, borderLeft: `2px solid ${c.ring}`, borderRadius: '12px 0 0 0' }} />
                <div style={{ position: 'absolute', top: 0, right: 0, width: 20, height: 20, borderTop: `2px solid ${c.ring}`, borderRight: `2px solid ${c.ring}`, borderRadius: '0 12px 0 0' }} />
                <div style={{ position: 'absolute', bottom: 0, left: 0, width: 20, height: 20, borderBottom: `2px solid ${c.ring}`, borderLeft: `2px solid ${c.ring}`, borderRadius: '0 0 0 12px' }} />
                <div style={{ position: 'absolute', bottom: 0, right: 0, width: 20, height: 20, borderBottom: `2px solid ${c.ring}`, borderRight: `2px solid ${c.ring}`, borderRadius: '0 0 12px 0' }} />
            </>}

            <div style={{ textAlign: 'center' }}>
                {file ? (
                    <>
                        <div style={{
                            width: 56, height: 56, borderRadius: 16,
                            background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            margin: '0 auto 16px', fontSize: 24
                        }}>✓</div>
                        <div style={{ color: '#6ee7b7', fontFamily: 'Syne', fontWeight: 600, fontSize: 15, marginBottom: 4 }}>
                            {file.name.length > 28 ? file.name.slice(0, 25) + '...' : file.name}
                        </div>
                        <div style={{ color: 'rgba(100,116,139,0.8)', fontSize: 13 }}>
                            {(file.size / 1024).toFixed(1)} KB · Click to change
                        </div>
                    </>
                ) : (
                    <>
                        <div style={{
                            width: 56, height: 56, borderRadius: 16,
                            background: `rgba(${color === 'indigo' ? '99,102,241' : '139,92,246'},0.1)`,
                            border: `1px solid ${c.ring}`,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            margin: '0 auto 16px', fontSize: 26,
                            boxShadow: `0 0 20px ${c.glow}`
                        }}>{icon}</div>
                        <div style={{ fontFamily: 'Syne', fontWeight: 600, color: '#e2e8f0', fontSize: 15, marginBottom: 6 }}>{label}</div>
                        <div style={{ color: 'rgba(148,163,184,0.6)', fontSize: 13, marginBottom: 8 }}>{sublabel}</div>
                        <div style={{
                            display: 'inline-flex', alignItems: 'center', gap: 6,
                            background: `rgba(${color === 'indigo' ? '99,102,241' : '139,92,246'},0.08)`,
                            border: `1px solid rgba(${color === 'indigo' ? '99,102,241' : '139,92,246'},0.2)`,
                            borderRadius: 8, padding: '4px 12px',
                            color: c.text, fontSize: 12, fontWeight: 500
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
            {/* Floating orbs */}
            <FloatingOrb style={{ width: 600, height: 600, top: -200, left: -200 }} />
            <FloatingOrb style={{ width: 400, height: 400, bottom: -100, right: -100, background: 'radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%)' }} />

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

            {/* Main */}
            <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 24px' }}>
                <div style={{ maxWidth: 640, width: '100%' }} className="animate-fade-up">

                    {/* Badge */}
                    <div style={{ textAlign: 'center', marginBottom: 32 }}>
                        <div style={{
                            display: 'inline-flex', alignItems: 'center', gap: 8,
                            background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)',
                            borderRadius: 24, padding: '6px 16px', marginBottom: 24
                        }}>
                            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#6366f1', boxShadow: '0 0 8px #6366f1', animation: 'glow-pulse 2s ease-in-out infinite' }} />
                            <span style={{ fontSize: 12, color: '#a5b4fc', fontWeight: 500 }}>Powered by AI · Zero Hallucinations · WGT Algorithm</span>
                        </div>

                        <h1 style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: 'clamp(36px,5vw,52px)', lineHeight: 1.1, marginBottom: 16 }}>
                            Your Personalized<br />
                            <span className="gradient-text">Learning Path</span><br />
                            <span style={{ color: 'rgba(226,232,240,0.85)' }}>Starts Here</span>
                        </h1>
                        <p style={{ color: 'rgba(148,163,184,0.75)', fontSize: 16, lineHeight: 1.7, maxWidth: 480, margin: '0 auto' }}>
                            Upload your resume and a job description. Our AI analyzes skill gaps
                            and generates a prioritized roadmap in under 30 seconds.
                        </p>
                    </div>

                    {/* Upload zones */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }} className="animate-fade-up delay-200">
                        <div>
                            <div style={{ fontSize: 11, fontWeight: 600, color: 'rgba(165,180,252,0.6)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 8, paddingLeft: 4 }}>
                                01 · Your Resume
                            </div>
                            <DropZone label="Upload Resume" sublabel="Your work history & skills" icon="📄" file={resumeFile} onDrop={setResumeFile} color="indigo" />
                        </div>
                        <div>
                            <div style={{ fontSize: 11, fontWeight: 600, color: 'rgba(196,181,253,0.6)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 8, paddingLeft: 4 }}>
                                02 · Job Description
                            </div>
                            <DropZone label="Upload Job Description" sublabel="Target role requirements" icon="💼" file={jdFile} onDrop={setJdFile} color="violet" />
                        </div>
                    </div>

                    {/* CTA */}
                    <div className="animate-fade-up delay-300">
                        <button
                            onClick={handleAnalyze}
                            disabled={!canAnalyze}
                            style={{
                                width: '100%', padding: '16px 32px', borderRadius: 16,
                                border: 'none', cursor: canAnalyze ? 'pointer' : 'not-allowed',
                                fontSize: 16, fontFamily: 'Syne', fontWeight: 700, letterSpacing: '0.02em',
                                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
                                transition: 'all 0.3s ease',
                                background: canAnalyze
                                    ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%)'
                                    : 'rgba(255,255,255,0.05)',
                                color: canAnalyze ? 'white' : 'rgba(148,163,184,0.4)',
                                boxShadow: canAnalyze ? '0 0 40px rgba(99,102,241,0.35), 0 8px 32px rgba(99,102,241,0.2)' : 'none',
                                transform: canAnalyze ? 'translateY(0)' : 'none',
                            }}
                            onMouseEnter={e => { if (canAnalyze) { e.target.style.transform = 'translateY(-2px)'; e.target.style.boxShadow = '0 0 60px rgba(99,102,241,0.5), 0 12px 40px rgba(99,102,241,0.3)' } }}
                            onMouseLeave={e => { if (canAnalyze) { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 0 40px rgba(99,102,241,0.35), 0 8px 32px rgba(99,102,241,0.2)' } }}
                        >
                            ⚡ Analyze My Skill Gap →
                        </button>
                    </div>

                    {/* Feature pills */}
                    <div style={{ display: 'flex', justifyContent: 'center', gap: 12, marginTop: 24, flexWrap: 'wrap' }} className="animate-fade-up delay-400">
                        {[
                            ['⚡', 'Under 30 seconds'],
                            ['🎯', 'Zero hallucinations'],
                            ['🔍', 'Full reasoning traces'],
                            ['📊', 'WGT algorithm'],
                        ].map(([icon, text]) => (
                            <div key={text} style={{
                                display: 'flex', alignItems: 'center', gap: 6,
                                background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                                borderRadius: 20, padding: '6px 14px', fontSize: 12, color: 'rgba(148,163,184,0.7)'
                            }}>
                                <span style={{ fontSize: 14 }}>{icon}</span> {text}
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    )
}
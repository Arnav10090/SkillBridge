import useAppStore from './store/useAppStore'
import UploadScreen from './components/UploadScreen'
import ProcessingScreen from './components/ProcessingScreen'
import ResultsDashboard from './components/ResultsDashboard'
import RoadmapView from './components/RoadmapView'

// Placeholder components (we'll build these next)
if (!window.__placeholders) {
  window.__placeholders = true
}

export default function App() {
  const { step, error, reset } = useAppStore()

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      {error && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-red-500/10 border border-red-500/30 text-red-300 px-6 py-3 rounded-xl flex items-center gap-3 shadow-xl">
          <span className="text-sm">{error}</span>
          <button onClick={reset} className="text-red-400 hover:text-red-200 font-bold text-lg leading-none">×</button>
        </div>
      )}

      {step === 'upload' && <UploadScreen />}
      {step === 'processing' && <ProcessingScreen />}
      {step === 'results' && <ResultsDashboard />}
      {step === 'roadmap' && <RoadmapView />}
    </div>
  )
}
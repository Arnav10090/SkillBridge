import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAppStore = create(
  persist(
    (set) => ({
      // State
      step: 'upload',
      jobId: null,
      jobStatus: null,
      progress: 0,
      statusMessage: '',
      results: null,
      error: null,
      activeSkillId: null,

      // Actions
      setStep:          (step)   => set({ step }),
      setJobId:         (jobId)  => set({ jobId }),
      setProgress:      (p, msg) => set({ progress: p, statusMessage: msg }),
      setResults:       (data)   => set({ results: data, step: 'results' }),
      setError:         (err)    => set({ error: err, step: 'upload' }),
      setActiveSkillId: (id)     => set({ activeSkillId: id }),
      reset: () => set({
        step: 'upload', jobId: null, jobStatus: null,
        progress: 0, statusMessage: '', results: null,
        error: null, activeSkillId: null
      }),
    }),
    {
      name: 'skillbridge-state',         // localStorage key
      partialize: (state) => ({          // only persist what matters
        step:    state.step === 'processing' ? 'upload' : state.step,
        results: state.results,
        jobId:   state.jobId,
      }),
    }
  )
)

export default useAppStore
<template>
  <div class="roadmap-viewer">
    <div class="roadmap-header">
      <div class="d-flex justify-content-between align-items-center">
        <h3 class="mb-0">
          <i class="bi bi-map me-2"></i>
          Project Roadmap
        </h3>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-primary btn-hover" @click="fetchRoadmap" :disabled="loading">
            <i class="bi bi-arrow-clockwise me-1" :class="{ 'rotating': loading }"></i>
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
          <button class="btn btn-sm btn-primary btn-gradient" @click="generateNewRoadmap" :disabled="generating">
            <i class="bi bi-plus-circle me-1"></i>
            {{ generating ? 'Generating...' : 'Generate New' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary loading-spinner" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted fw-semibold">Loading roadmap...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger custom-alert" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <div v-else-if="roadmap" class="roadmap-content">
      <div class="roadmap-section">
        <div class="summary-card">
          <h5><i class="bi bi-info-circle me-2"></i>Summary</h5>
          <p>{{ roadmap.summary }}</p>

          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ roadmap.total_requirements || 0 }}</div>
              <div class="stat-label">Total Requirements</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ roadmap.milestones?.length || 0 }}</div>
              <div class="stat-label">Milestones</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ roadmap.timeline?.total_estimated_days || 0 }}</div>
              <div class="stat-label">Estimated Days</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ roadmap.completed_count || 0 }}</div>
              <div class="stat-label">Completed</div>
            </div>
          </div>
        </div>
      </div>

      <div class="roadmap-section">
        <h5><i class="bi bi-calendar3 me-2"></i>Timeline</h5>
        <div class="timeline-card">
          <div class="timeline-info">
            <div class="timeline-item">
              <span class="label">Start Date:</span>
              <span class="value">{{ formatDate(roadmap.timeline?.start_date) }}</span>
            </div>
            <div class="timeline-item">
              <span class="label">Estimated Completion:</span>
              <span class="value">{{ formatDate(roadmap.timeline?.estimated_completion_date) }}</span>
            </div>
            <div class="timeline-item">
              <span class="label">Duration:</span>
              <span class="value">{{ roadmap.timeline?.total_estimated_days || 0 }} days</span>
            </div>
          </div>
        </div>
      </div>

      <div class="roadmap-section">
        <h5><i class="bi bi-flag me-2"></i>Milestones</h5>
        <div class="milestones-container">
          <div v-for="(milestone, index) in roadmap.milestones" :key="index" class="milestone-card">
            <div class="milestone-header">
              <div class="milestone-number">{{ index + 1 }}</div>
              <div class="milestone-info">
                <h6 class="milestone-title">{{ milestone.milestone_name }}</h6>
                <p class="milestone-description">{{ milestone.description }}</p>
              </div>
            </div>
            <div class="milestone-meta">
              <span class="badge bg-primary">
                <i class="bi bi-calendar-event me-1"></i>
                {{ milestone.estimated_days || 0 }} days
              </span>
              <span class="badge bg-info">
                <i class="bi bi-list-task me-1"></i>
                {{ milestone.requirements?.length || 0 }} requirements
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="roadmap-section" v-if="roadmap.workflow_steps && roadmap.workflow_steps.length > 0">
        <h5><i class="bi bi-diagram-3 me-2"></i>Workflow Steps</h5>
        <div class="workflow-container">
          <div v-for="(workflow, index) in roadmap.workflow_steps" :key="index" class="workflow-milestone">
            <h6 class="workflow-milestone-title">
              Milestone {{ workflow.milestone_id }} Steps
            </h6>
            <div class="workflow-steps">
              <div v-for="(step, stepIndex) in workflow.steps" :key="stepIndex" class="workflow-step">
                <div class="step-number">{{ stepIndex + 1 }}</div>
                <div class="step-content">
                  <h6 class="step-name">{{ step.step_name }}</h6>
                  <p class="step-description">{{ step.description }}</p>
                  <div class="step-meta">
                    <span class="badge bg-secondary">{{ step.responsible_role }}</span>
                    <span class="badge bg-light text-dark">
                      <i class="bi bi-clock me-1"></i>
                      {{ step.estimated_hours }}h
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="roadmap-section">
        <h5><i class="bi bi-lightbulb me-2"></i>Recommendations</h5>
        <div class="recommendations-container">
          <div v-for="(recommendation, index) in roadmap.recommendations" :key="index" class="recommendation-item">
            <i class="bi bi-check-circle-fill recommendation-icon"></i>
            <span>{{ recommendation }}</span>
          </div>
        </div>
      </div>

      <div class="roadmap-footer">
        <small class="text-muted">
          <i class="bi bi-info-circle me-1"></i>
          Version {{ roadmap.version || 1 }} • Generated {{ formatDate(roadmap.generated_at) }}
        </small>
      </div>
    </div>

    <div v-else class="text-center py-5 no-roadmap-state">
      <div class="empty-state-icon">
        <i class="bi bi-map"></i>
      </div>
      <p class="mt-3 text-muted fw-semibold fs-5">No roadmap available</p>
      <p class="text-muted mb-4">Generate your first roadmap to visualize the project timeline</p>
      <button class="btn btn-primary btn-gradient btn-lg" @click="generateNewRoadmap">
        <i class="bi bi-plus-circle me-2"></i>
        Generate Roadmap
      </button>
    </div>
  </div>
</template>

<script>
import { make_getrequest, make_postrequest } from '@/store/appState';
import { useNotify } from '@/utils/useNotify';

export default {
  name: 'ProductManagerRoadmap',
  props: {
    projectId: {
      type: [String, Number],
      required: true
    },
    clientId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      roadmap: null,
      loading: false,
      generating: false,
      error: null
    };
  },
  setup() {
    const notify = useNotify();
    return { notify };
  },
  methods: {
    async fetchRoadmap() {
      this.loading = true;
      this.error = null;

      try {
        const response = await make_getrequest(
          `/api/pm/project/${this.projectId}/client/${this.clientId}/roadmap`
        );

        if (response && response.data) {
          this.roadmap = response.data.data || response.data;
        } else {
          this.error = 'Failed to load roadmap';
        }
      } catch (error) {
        console.error('Error fetching roadmap:', error);
        this.error = error.message || 'Failed to load roadmap';
      } finally {
        this.loading = false;
      }
    },
    async generateNewRoadmap() {
      this.generating = true;
      this.error = null;

      try {
        const response = await make_postrequest(
          `/api/pm/project/${this.projectId}/client/${this.clientId}/roadmap`,
          {
            trigger_type: 'manual',
            send_email: true
          }
        );

        if (response && response.data) {
          this.roadmap = response.data.data || response.data;
          this.notify.success('Roadmap generated successfully! Check your email for details.');
        } else {
          this.error = 'Failed to generate roadmap';
          this.notify.error('Failed to generate roadmap');
        }
      } catch (error) {
        console.error('Error generating roadmap:', error);
        this.error = error.message || 'Failed to generate roadmap';
        this.notify.error(this.error);
      } finally {
        this.generating = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      } catch (e) {
        return dateString;
      }
    }
  },
  mounted() {
    this.fetchRoadmap();
  },
  watch: {
    projectId() {
      this.fetchRoadmap();
    },
    clientId() {
      this.fetchRoadmap();
    }
  }
}
</script>

<style scoped>
.roadmap-viewer {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.roadmap-header {
  padding-bottom: 20px;
  border-bottom: 3px solid rgba(102, 126, 234, 0.3);
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.roadmap-header h3 {
  color: #667eea;
  font-weight: 700;
  font-size: 28px;
}

.roadmap-content {
  max-height: 75vh;
  overflow-y: auto;
  padding-right: 10px;
}

.roadmap-section {
  margin-bottom: 35px;
}

.roadmap-section h5 {
  color: #667eea;
  margin-bottom: 20px;
  font-weight: 700;
  font-size: 22px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.roadmap-section h5::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
}

.summary-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
}

.summary-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.summary-card h5 {
  color: white;
  margin-bottom: 15px;
  font-size: 24px;
  font-weight: 700;
}

.summary-card p {
  font-size: 17px;
  line-height: 1.7;
  margin-bottom: 25px;
  opacity: 0.95;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.stat-item {
  background-color: rgba(255, 255, 255, 0.25);
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
  background-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 14px;
  opacity: 0.95;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.timeline-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  border-left: 5px solid #667eea;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.timeline-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
  transform: translateX(5px);
}

.timeline-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.timeline-item .label {
  font-weight: 600;
  color: #667eea;
}

.timeline-item .value {
  color: #333;
}

.milestones-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.milestone-card {
  background: white;
  border: none;
  border-left: 6px solid #667eea;
  padding: 25px;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  position: relative;
}

.milestone-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px 0 0 12px;
}

.milestone-card:hover {
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
  transform: translateX(8px);
  border-left-color: #764ba2;
}

.milestone-header {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 15px;
}

.milestone-number {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: bold;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
  position: relative;
}

.milestone-number::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid rgba(102, 126, 234, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {

  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
}

.milestone-info {
  flex: 1;
}

.milestone-title {
  color: #2d3748;
  margin-bottom: 10px;
  font-weight: 700;
  font-size: 18px;
}

.milestone-description {
  color: #718096;
  margin: 0;
  line-height: 1.6;
  font-size: 15px;
}

.milestone-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.workflow-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-milestone {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.workflow-milestone-title {
  color: #667eea;
  margin-bottom: 15px;
  font-weight: 600;
}

.workflow-steps {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.workflow-step {
  background-color: white;
  padding: 15px;
  border-radius: 6px;
  border-left: 3px solid #667eea;
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.step-number {
  background-color: #667eea;
  color: white;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.step-description {
  color: #666;
  margin-bottom: 10px;
  font-size: 14px;
}

.step-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.recommendations-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
  border-left: 5px solid #ffc107;
  padding: 18px 20px;
  border-radius: 10px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  font-size: 15px;
  line-height: 1.7;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
  transition: all 0.3s ease;
}

.recommendation-item:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
}

.recommendation-icon {
  color: #ffc107;
  font-size: 22px;
  flex-shrink: 0;
  margin-top: 2px;
}

.roadmap-footer {
  margin-top: 40px;
  padding-top: 25px;
  border-top: 2px solid rgba(102, 126, 234, 0.2);
  text-align: center;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.roadmap-footer small {
  font-size: 14px;
  color: #718096;
  font-weight: 500;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .timeline-item {
    flex-direction: column;
    gap: 5px;
  }

  .milestone-header {
    flex-direction: column;
  }

  .workflow-step {
    flex-direction: column;
  }
}

.roadmap-content::-webkit-scrollbar {
  width: 10px;
}

.roadmap-content::-webkit-scrollbar-track {
  background: rgba(241, 241, 241, 0.5);
  border-radius: 10px;
}

.roadmap-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.roadmap-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.workflow-container {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.workflow-step {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  padding: 18px;
  border-radius: 10px;
  border-left: 4px solid #667eea;
  display: flex;
  gap: 15px;
  align-items: flex-start;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.workflow-step:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.step-number {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: bold;
  flex-shrink: 0;
  box-shadow: 0 3px 8px rgba(102, 126, 234, 0.3);
}

.btn-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.btn-hover {
  transition: all 0.3s ease;
}

.btn-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.2);
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border-width: 0.3rem;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.no-roadmap-state {
  background: white;
  border-radius: 15px;
  padding: 60px 40px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.empty-state-icon {
  font-size: 5rem;
  color: #667eea;
  opacity: 0.3;
  margin-bottom: 20px;
}

.custom-alert {
  border-radius: 10px;
  border: none;
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
  font-weight: 500;
}

.badge {
  padding: 8px 12px;
  font-weight: 600;
  font-size: 13px;
}
</style>
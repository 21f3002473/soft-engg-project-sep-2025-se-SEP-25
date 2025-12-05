<template>
  <div class="container-fluid my-3" style="max-width: 1000px;">
    <div class="card border-0 shadow-sm rounded-4 h-100" style="background-color: #f9fbff; min-height: 600px;">
      <div class="card-body d-flex flex-column p-4">
        
        <div class="mb-4 text-start">
          <h2 class="fw-bold text-primary mb-1" style="font-size: 22px;">Quick Notes</h2>
          <p class="text-muted small mb-0">Jot down your thoughts, tasks, or reminders — all in one place.</p>
        </div>

        <div class="row g-4 flex-fill" style="min-height: 0;">
          
          <div class="col-md-3 d-flex flex-column border-end pe-3">
            <button class="btn btn-primary w-100 mb-3 d-flex align-items-center justify-content-center" @click="createNewNote">
              <i class="bi bi-plus-lg me-2"></i>New Note
            </button>
            
            <div v-if="loading" class="text-center py-3 text-muted">
              <div class="spinner-border spinner-border-sm" role="status"></div>
            </div>
            
            <div v-else-if="notes.length === 0" class="text-center py-3 text-muted">
              <small>No notes yet.</small>
            </div>

            <div class="list-group list-group-flush overflow-auto flex-fill" v-else>
              <button 
                v-for="note in notes" 
                :key="note.id" 
                class="list-group-item list-group-item-action border-0 rounded-2 mb-2 d-flex justify-content-between align-items-start p-3"
                :class="{ 'active-note': note.id === selectedNoteId }"
                @click="selectNote(note)"
                style="transition: background 0.2s;"
              >
                <div class="d-flex flex-column overflow-hidden w-100">
                  <span class="fw-semibold text-truncate" style="font-size: 14px;">{{ note.topic || 'Untitled Note' }}</span>
                  <span class="text-muted text-truncate small">{{ getPreview(note.notes) }}</span>
                </div>
                <span class="text-danger ms-2 delete-icon" @click.stop="confirmDelete(note.id)" title="Delete Note">
                  <i class="bi bi-trash"></i>
                </span>
              </button>
            </div>
          </div>

          <div class="col-md-9 d-flex flex-column">
            
            
            <input 
              v-model="topic" 
              placeholder="Note Topic" 
              class="form-control fw-bold mb-3"
              style="font-size: 16px;"
            />
            
            <textarea
              v-model="text"
              placeholder="Start typing your notes here..."
              class="form-control flex-fill mb-3"
              style="resize: none; font-size: 15px; line-height: 1.6;"
            ></textarea>

            <div class="d-flex justify-content-end align-items-center gap-2">
              
              <button @click="saveNote" class="btn btn-primary px-4" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
              <button @click="clearText" class="btn btn-light border px-4">Clear</button>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_getrequest, make_postrequest, make_putrequest, make_deleterequest } from '@/store/appState.js';
import { useNotify } from "@/utils/useNotify.js";
import Swal from 'sweetalert2';

export default {
  name: 'EmployeeWriting',
  data() {
    return {
      notes: [],
      selectedNoteId: null,
      topic: '',
      text: '',
      loading: false,
      saving: false,
    };
  },
  mounted() {
    this.fetchNotes();
  },
  methods: {
    async fetchNotes() {
      this.loading = true;
      try {
        const response = await make_getrequest('/api/employee/writing');
        this.notes = response.notes;
      } catch (err) {
        console.error('Failed to fetch notes:', err);
        useNotify().error('Failed to load notes.');
      } finally {
        this.loading = false;
      }
    },
    selectNote(note) {
      this.selectedNoteId = note.id;
      this.topic = note.topic;
      this.text = note.notes;
    },
    createNewNote() {
      this.selectedNoteId = null;
      this.topic = '';
      this.text = '';
    },
    getPreview(text) {
      if (!text) return 'No content';
      return text.length > 30 ? text.substring(0, 30) + '...' : text;
    },
    async saveNote() {
      if (!this.text.trim()) {
        useNotify().warn('Note content cannot be empty.');
        return;
      }
      
      this.saving = true;

      try {
        const payload = {
          topic: this.topic || 'Untitled Note',
          notes: this.text
        };

        if (this.selectedNoteId) {
          await make_putrequest(`/api/employee/writing/${this.selectedNoteId}`, payload);
          useNotify().success('Note updated successfully.');
          
          const index = this.notes.findIndex(n => n.id === this.selectedNoteId);
          if (index !== -1) {
            this.notes[index] = { ...this.notes[index], ...payload };
          }
        } else {
          const response = await make_postrequest('/api/employee/writing', payload);
          useNotify().success('Note saved successfully.');
          this.selectedNoteId = response.id;
          
          this.notes.push({ id: response.id, ...payload });
        }
        
      } catch (err) {
        console.error('Failed to save note:', err);
        useNotify().error('Failed to save note. Please try again.');
      } finally {
        this.saving = false;
      }
    },
    async confirmDelete(id) {
      const result = await Swal.fire({
        title: 'Delete Note?',
        text: "Are you sure you want to delete this note?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
      });

      if (result.isConfirmed) {
        try {
          await make_deleterequest(`/api/employee/writing/${id}`);
          this.notes = this.notes.filter(n => n.id !== id);
          if (this.selectedNoteId === id) {
            this.createNewNote();
          }
          useNotify().info('Note deleted.');
        } catch (err) {
          console.error('Failed to delete note:', err);
          useNotify().error('Failed to delete note.');
        }
      }
    },
    async clearText() {
        const result = await Swal.fire({
        title: 'Clear Text?',
        text: "This will clear the current editor. Are you sure?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, clear it!'
      });

      if (result.isConfirmed) {
        this.text = '';
      }
    }
  }
};
</script>

<style scoped>
.active-note {
  background-color: #e6f0ff !important;
  border: 1px solid #b3d1ff !important;
}

.list-group-item:hover {
  background-color: #f0f4f8;
}

.delete-icon {
  opacity: 0;
  cursor: pointer;
  transition: opacity 0.2s;
}

.list-group-item:hover .delete-icon {
  opacity: 1;
}

.list-group::-webkit-scrollbar {
  width: 6px;
}
.list-group::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 4px;
}
</style>
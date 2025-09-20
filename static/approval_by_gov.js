// ✅ Correct Supabase import
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/esm/supabase.js";

// ✅ Correct variable usage
const supabaseUrl = "https://fuytavhlulrlimlonmst.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1eXRhdmhsdWxybGltbG9ubXN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcyNjE5MDgsImV4cCI6MjA3MjgzNzkwOH0.zPVmj7wVtj9J8hfGwi816uW2dcQsJ8Pv4UjSE4IuA-M";

const supabase = createClient(supabaseUrl, supabaseKey);

let doctors = [];
let filteredDoctors = [];

// ✅ Wait for DOM to be ready before doing anything
document.addEventListener("DOMContentLoaded", () => {
    console.log("Initializing Doctor Verification Dashboard...");
    fetchDoctors();

    // Attach listeners AFTER DOM exists
    document.getElementById('searchInput').addEventListener('input', filterDoctors);
    document.getElementById('statusFilter').addEventListener('change', filterDoctors);
    document.getElementById('specializationFilter').addEventListener('change', filterDoctors);

    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelectorAll('.menu-item').forEach(menu => menu.classList.remove('active'));
            this.classList.add('active');
        });
    });
});


// Fetch doctors from Supabase
async function fetchDoctors() {
    try {
        const { data, error } = await supabase
            .from('doctors')
            .select('id, full_name, email, license_number, specialization, status, created_at')
            .order('created_at', { ascending: false });

        if (error) {
            console.error('Error fetching doctors:', error.message);
            showError('Failed to load doctors list.');
            return;
        }

        doctors = data.map((doc) => ({
            id: doc.id,
            name: doc.full_name,
            email: doc.email,
            license: doc.license_number,
            specialization: doc.specialization,
            status: doc.status,
            created_at: doc.created_at
        }));

        filteredDoctors = [...doctors];
        updateStats();
        renderTable();
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to database.');
    }
}

function updateStats() {
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    
    const thisMonthDoctors = doctors.filter(d => 
        new Date(d.created_at) >= startOfMonth
    );

    const pending = doctors.filter(d => d.status === 'pending').length;
    const approved = thisMonthDoctors.filter(d => d.status === 'approved').length;
    const rejected = thisMonthDoctors.filter(d => d.status === 'rejected').length;

    document.getElementById('pendingCount').textContent = pending;
    document.getElementById('approvedCount').textContent = approved;
    document.getElementById('rejectedCount').textContent = rejected;
}

function renderTable() {
    const tbody = document.getElementById('tableBody');
    
    if (filteredDoctors.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5">
                    <div class="empty-state">
                        <i class="fas fa-search"></i>
                        <h3>No doctors found</h3>
                        <p>No doctors match your search criteria. Try adjusting your filters.</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filteredDoctors.map(doctor => `
        <tr>
            <td>
                <div class="doctor-name">${doctor.name}</div>
                <div class="doctor-email">${doctor.email}</div>
            </td>
            <td><span class="license-number">${doctor.license}</span></td>
            <td><span class="specialization">${doctor.specialization}</span></td>
            <td><span class="status ${doctor.status}">${doctor.status}</span></td>
            <td>
                <div class="action-buttons">
                    ${doctor.status === 'pending' ? `
                        <button class="btn btn-approve" onclick="approveDoctor('${doctor.id}')">
                            <i class="fas fa-check"></i> Approve
                        </button>
                        <button class="btn btn-reject" onclick="rejectDoctor('${doctor.id}')">
                            <i class="fas fa-times"></i> Reject
                        </button>
                    ` : `
                        <button class="btn btn-view" onclick="viewDoctor('${doctor.id}')">
                            <i class="fas fa-eye"></i> View
                        </button>
                    `}
                </div>
            </td>
        </tr>
    `).join('');
}

// ✅ Approve Doctor (FIXED)
window.approveDoctor = async function(id) {
    const doctor = doctors.find(d => d.id === id);
    if (!doctor) return;

    if (!confirm(`Are you sure you want to APPROVE Dr. ${doctor.name}'s application?`)) return;

    try {
        const { error } = await supabase
            .from('doctors')
            .update({ 
                status: 'approved',
                gov_reviewed_at: new Date().toISOString()
            })
            .eq('id', id);

        if (error) {
            showError("Error approving doctor: " + error.message);
            return;
        }

        showSuccess(`✅ Dr. ${doctor.name} has been approved.`);
        await fetchDoctors();
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to approve doctor.');
    }
};

// ✅ Reject Doctor (Separate Function)
window.rejectDoctor = async function(id) {
    const doctor = doctors.find(d => d.id === id);
    if (!doctor) return;

    if (!confirm(`Are you sure you want to REJECT Dr. ${doctor.name}'s application?`)) return;

    try {
        const { error } = await supabase
            .from('doctors')
            .update({ 
                status: 'rejected',
                gov_reviewed_at: new Date().toISOString()
            })
            .eq('id', id);

        if (error) {
            showError("Error rejecting doctor: " + error.message);
            return;
        }

        showSuccess(`❌ Dr. ${doctor.name} has been rejected.`);
        await fetchDoctors();
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to reject doctor.');
    }
};

window.viewDoctor = function(id) {
    const doctor = doctors.find(d => d.id === id);
    if (!doctor) return;

    alert(`Doctor Details:\n\nName: ${doctor.name}\nEmail: ${doctor.email}\nLicense: ${doctor.license}\nSpecialization: ${doctor.specialization}\nStatus: ${doctor.status}`);
};

function filterDoctors() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const specializationFilter = document.getElementById('specializationFilter').value;

    filteredDoctors = doctors.filter(doctor => {
        const matchesSearch = doctor.name.toLowerCase().includes(searchTerm) ||
            doctor.license.toLowerCase().includes(searchTerm) ||
            doctor.email.toLowerCase().includes(searchTerm) ||
            doctor.specialization.toLowerCase().includes(searchTerm);

        const matchesStatus = statusFilter === 'all' || doctor.status === statusFilter;
        const matchesSpecialization = specializationFilter === 'all' || 
            doctor.specialization.toLowerCase() === specializationFilter;

        return matchesSearch && matchesStatus && matchesSpecialization;
    });

    renderTable();
}

// ✅ Success + Error Notification Functions stay same
function showSuccess(message) { /* ... same as before ... */ }
function showError(message) { /* ... same as before ... */ }

// Event listeners
document.getElementById('searchInput').addEventListener('input', filterDoctors);
document.getElementById('statusFilter').addEventListener('change', filterDoctors);
document.getElementById('specializationFilter').addEventListener('change', filterDoctors);

// Logout function
window.handleLogout = function() {
    if (confirm('Are you sure you want to logout?')) {
        showSuccess('Logout successful!');
        // Add your logout logic here
    }
};

// Navigation handlers
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelectorAll('.menu-item').forEach(menu => menu.classList.remove('active'));
        this.classList.add('active');
    });
});

// Initialize
fetchDoctors();

// In approval_by_gov.js (top level)
document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing Doctor Verification Dashboard...");
  fetchDoctors(); // <-- call your function here
});
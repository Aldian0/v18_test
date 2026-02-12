from odoo import models, fields, api
import json

class ProjectBudgetWizard(models.TransientModel):
    _name = 'project.budget.wizard'
    _description = 'Wizard Kalkulasi Budget Hierarkis'

    # Field untuk menampilkan hasil di layar
    result_text = fields.Text(string="Hasil Perhitungan", readonly=True)
    raw_data_display = fields.Text(string="Data JSON Input", readonly=True)

    def action_calculate_budget(self):
        """
        Action yang dipanggil saat tombol diklik.
        Mendefinisikan data soal dan memanggil fungsi hitung.
        """
        # 1. Data Input (Sesuai Soal)
        projects_data = [
            {
                "name": "Project Alpha",
                "budget": 10000,
                "sub_projects": [
                    {
                        "name": "Alpha-1",
                        "budget": 5000,
                        "sub_projects": []
                    },
                    {
                        "name": "Alpha-2",
                        "budget": 3000,
                        "sub_projects": [
                            {
                                "name": "Alpha-2-A",
                                "budget": 1000,
                                "sub_projects": []
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Project Beta",
                "budget": 8000,
                "sub_projects": []
            }
        ]

        # 2. Panggil Fungsi Rekursif
        total_budget = self._calculate_total_budget_recursive(projects_data)

        # 3. Tampilkan Hasil
        self.raw_data_display = json.dumps(projects_data, indent=2)
        self.result_text = (
            f"Total Project Alpha & Sub: 19,000\n"
            f"Total Project Beta: 8,000\n"
            f"---------------------------\n"
            f"GRAND TOTAL HITUNGAN SISTEM: {total_budget:,.0f}"
        )

        # Return action untuk refresh view (agar field terisi)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.budget.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _calculate_total_budget_recursive(self, projects):
        """
        Fungsi Rekursif untuk menghitung total anggaran.
        """
        total = 0
        
        for project in projects:
            # 1. Ambil budget project level ini
            current_budget = project.get('budget', 0)
            
            # 2. Cek apakah punya anak (sub_projects)
            sub_total = 0
            if project.get('sub_projects'):
                # REKURSI: Panggil fungsi ini sendiri untuk anak-anaknya
                sub_total = self._calculate_total_budget_recursive(project['sub_projects'])
            
            # 3. Akumulasi total
            total += current_budget + sub_total
            
        return total
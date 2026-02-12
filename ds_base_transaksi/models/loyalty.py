from odoo import models, fields, api
from datetime import datetime

class LoyaltyAnalysis(models.Model):
    _name = 'loyalty.analysis'
    _description = 'Analisis Loyalitas Pelanggan'

    name = fields.Char(string='Nama Pelanggan', required=True)
    transaction_ids = fields.One2many('loyalty.transaction', 'analysis_id', string='Daftar Transaksi')
    
    total_points = fields.Integer(string='Total Poin', readonly=True)
    max_discount = fields.Selection([
        ('NONE', 'None (0%)'),
        ('REGULAR', 'Regular (5%)'),
        ('PREMIUM', 'Premium (10%)'),
        ('SUPER_VIP', 'Super VIP (20%)')
    ], string='Diskon Maksimum', readonly=True, default='NONE')
    
    high_value_count = fields.Integer(string='Jumlah Transaksi Tinggi', readonly=True)
    failed_count = fields.Integer(string='Jumlah Transaksi Gagal', compute='_compute_failed_count')

    @api.depends('transaction_ids.status')
    def _compute_failed_count(self):
        for record in self:
            record.failed_count = len(record.transaction_ids.filtered(lambda t: t.status == 'failed'))
        
    def action_calculate_loyalty(self):
        """Update status transaksi menjadi failed jika poin 0 atau input nilai 0 di weekend"""
        for record in self:
            for tx in record.transaction_ids:
                # Lewati jika status memang sudah failed secara manual
                if tx.status == 'failed':
                    continue

                # Kondisi 1: Nilai > 500.000 (Syarat 5 Poin)
                is_high_value = tx.amount > 500000
                
                # Kondisi 2: Hari Sabtu (5) atau Minggu (6) (Syarat 3 Poin)
                is_weekend = tx.date and tx.date.weekday() in [5, 6]

                # Jika transaksi di weekend tapi nilai (amount) adalah 0 atau kurang, paksa jadi failed
                if is_weekend and tx.amount <= 0:
                    tx.status = 'failed'
                    continue

                # KONDISI UMUM: Jika tidak memenuhi syarat nilai tinggi DAN bukan weekend
                if not is_high_value and not is_weekend:
                    tx.status = 'failed'

            # Jalankan kalkulasi poin setelah status di-audit
            result = record.calculateLoyalty(record.transaction_ids)
            record.write({
                'total_points': result['totalPoints'],
                'max_discount': result['maxDiscount'],
                'high_value_count': result['highValueTransactionCount']
            })

    def calculateLoyalty(self, transactions):
        t_points = 0
        hv_count = 0
        for tx in transactions:
            # Transaksi status 'failed' (baik manual/otomatis) diabaikan
            if tx.status == 'failed':
                continue

            p_val = 5 if tx.amount > 500000 else 0
            if p_val == 5: hv_count += 1

            p_day = 3 if tx.date and tx.date.weekday() in [5, 6] else 0
            
            # Non-kumulatif: Ambil poin tertinggi
            t_points += max(p_val, p_day)

        # Penentuan Diskon
        discount = 'NONE'
        if t_points >= 50: discount = 'SUPER_VIP'
        elif t_points >= 20: discount = 'PREMIUM'
        elif t_points >= 10: discount = 'REGULAR'

        return {
            'totalPoints': t_points,
            'maxDiscount': discount,
            'highValueTransactionCount': hv_count
        }

class LoyaltyTransaction(models.Model):
    _name = 'loyalty.transaction'
    _description = 'Detail Transaksi'

    analysis_id = fields.Many2one('loyalty.analysis', ondelete='cascade')
    date = fields.Date(string='Tanggal', required=True, default=fields.Date.context_today)
    amount = fields.Float(string='Nilai Transaksi', required=True)
    status = fields.Selection([
        ('success', 'Berhasil'),
        ('failed', 'Gagal')
    ], string='Status', default='success', required=True)
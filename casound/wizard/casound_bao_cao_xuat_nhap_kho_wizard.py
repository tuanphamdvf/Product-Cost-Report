from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, AccessDenied, Warning
from datetime import date
from functools import reduce
import random
import datetime


class BaoCaoXuatNhapKho(models.TransientModel):
    _name = "casound.bao_cao_xuat_nhap_kho.wizard"
    _description = "Báo cáo xuất nhập kho"
    ngay_ton_start = fields.Date(string="Bắt đầu từ ngày", required=True)

    ngay_ton_end = fields.Date(string="Đến ngày", required=True)
    khohang = fields.Many2one('stock.location', string='Kho hàng', tracking=True, required=True, domain=[
        ('active', '=', True), ('usage', '=', 'view'), ('location_id', '!=', False)])

    # def get_location(self):
    #     hienthi = 'view'
    #     list_location = []
    #     list_location_main = self.env['product.product'].search(
    #         [('active', '=', True) and ('location', '!=', False) and ('usage', '=', hienthi)])
    #     keys_to_keep = ['id', 'complete_name']
    #     filtered_dict = {k: v for k, v in list_location_main.items() if k in keys_to_keep}
    #     if len(filtered_dict):
    #         for i in filtered_dict:
    #             list_location.append(tuple(i.items()))
    #     return list_location

    def print_report(self):
        print(self)
        product = "product"
        # danh sách sản phẩm và giá trị vốn
        list_product = self.env['product.template'].search(
            [('detailed_type', '=', product) and ('active', '=', True)])
        list_product_main = self.env['product.product'].search(
            [('active', '=', True) and ('detailed_type', '=', product)])
        list_kho_hang_main = self.env['stock.location'].search([('active', '=', True)])
        # giá trị vốn
        # list_unit_cost = self.env['stock.valuation.layer'].search([])
        # today = date.today().strftime("%d/%m/%Y")
        todayDate = datetime.date.today()
        if todayDate.day > 25:
            todayDate += datetime.timedelta(7)
        data = {
            'model': 'casound.bao_cao_xuat_nhap_kho.wizard',
            'form_data': self.read()[0]
        }
        ngay_ton_start = data['form_data']['ngay_ton_start']
        ngay_ton_end = data['form_data']['ngay_ton_end']
        diadiem = self.khohang
        listkhohang = []

        print(list_kho_hang_main)
        if len(list_kho_hang_main) != 0:
            for i in list_kho_hang_main:
                if i['location_id'] == diadiem.id:
                    listkhohang.append(i['location_id'])

        if ngay_ton_start != False and ngay_ton_end != False:
            data_list = self.env['stock.quant'].search(
                [
                    ('in_date', '>=', ngay_ton_start), ('in_date', '<=', ngay_ton_end)])
        else:
            data_list = self.env['stock.quant'].search(
                [('in_date', '>=', todayDate.replace(day=1)), ('in_date', '<=', todayDate)])

        list_san_pham = []
        danhsachphieu = []
        danhsachphieuchilds = []
        khohang = ''
        tongtondau = 0
        tongtoncuoi = 0
        tongthaydoi = 0
        tonggiatridau = 0
        tonggiatricuoi = 0
        tonggiatrithaydoi = 0

        tondau = 0
        toncuoi = 0
        if len(list_product_main) != 0:
            for i in list_product_main:
                vals = {
                    'name': i.name,
                    'masp': i.default_code,
                    'giavon': i['standard_price'],
                    'tondau': 0,
                    'toncuoi': 0,
                    'thaydoi': 0,
                    'giatridau': 0,
                    'giatricuoi': 0,
                    'giatrithaydoi': 0
                }
                danhsachthaydoi = i['stock_quant_ids']
                if len(danhsachthaydoi) != 0:
                    for j in danhsachthaydoi:
                        print(j['location_id'] in diadiem['child_ids'])
                        if (j['in_date'].date() <= ngay_ton_end) and (j['in_date'].date() >= ngay_ton_start):
                            danhsachphieu.append(j)
                        if len(diadiem['child_ids']) != 0:
                            for c in diadiem['child_ids']:
                                if len(danhsachphieu) != 0:
                                    for k in danhsachphieu:
                                        if c == k['location_id']:
                                            danhsachphieuchilds.append(k)
                                if len(danhsachphieuchilds) != 0:
                                    tondau += danhsachphieuchilds[0]['quantity']
                                    toncuoi += danhsachphieuchilds[-1]['quantity']
                                    print("tondau", tondau)
                                    print("toncuoi", toncuoi)

                                danhsachphieuchilds = []
                    if len(danhsachphieu) != 0:
                        #           tondau = danhsachphieu[0]['quantity']
                        # tondau = i['stock_quant_ids'][0]['quantity']
                        #          toncuoi = danhsachphieu[-1]['quantity']

                        tongtondau += tondau
                        tongtoncuoi += toncuoi
                        tongthaydoi += (toncuoi - tondau)
                        tonggiatridau += tondau * i['standard_price']
                        tonggiatricuoi += toncuoi * i['standard_price']
                        tonggiatrithaydoi += (toncuoi * i['standard_price']) - tondau * i['standard_price']
                    vals = {
                        'name': i.name,
                        'masp': i.default_code,
                        'giavon': i['standard_price'],
                        'tondau': tondau,
                        'toncuoi': toncuoi,
                        'thaydoi': toncuoi - tondau,
                        'giatridau': tondau * i['standard_price'],
                        'giatricuoi': toncuoi * i['standard_price'],
                        'giatrithaydoi': (toncuoi * i['standard_price']) - tondau * i['standard_price'],

                    }
                    danhsachphieu = []
                    tondau = 0
                    toncuoi = 0

                list_san_pham.append(vals)

        # if len(list_san_pham) != 0:
        #     for i in list_san_pham:
        #         print(i['name'])

        data['list_san_pham'] = list_san_pham
        data['ngay_ton_start'] = ngay_ton_start.strftime('%d/%m/%Y')
        data['ngay_ton_end'] = ngay_ton_end.strftime('%d/%m/%Y')
        data['tongtondau'] = tongtondau
        data['tongtoncuoi'] = tongtoncuoi
        data['tongthaydoi'] = tongthaydoi
        data['tonggiatridau'] = tonggiatridau
        data['tonggiatricuoi'] = tonggiatricuoi
        data['tonggiatrithaydoi'] = tonggiatrithaydoi
        data['khohang'] = diadiem['complete_name']
        print(data)
        return self.env.ref("casound.action_bao_cao_xuat_nhap_kho_report").report_action(self, data=data)

        # list_id = []
        # if len(list_product) != 0:
        #     for item in list_product:
        #         print(item)
        # list_unique = list(set(list_id))

        # result = []
        # if len(list_product_main) != 0:
        #     for i in list_product_main:
        #         print(i)
        #         print(i['id'])
        #         quant = self.env['stock.quant'].search([('id', '=', i['id'])])

        #         data = {
        #             'name': i.name,
        #             'giavon': i['standard_price'],
        #             'tondau': quant[0]['quantity'],
        #             'toncuoi': quant[-1]['quantity'],
        #             'thaydoi': quant[0]['quantity'] - quant[-1]['quantity'],

        #         }
        #         result.append(data)
        #         product = []

        # if len(data_list) != 0:
        #     for j in data_list:
        #         print(type(i.id), type(j.product_id))
        #         if j.product_id == int(i.id):
        #             product.append(j)
        #             unit_cost.append(j)
        #             print("danh sách", unit_cost)
        #             if len(product) != 0:

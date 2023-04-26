from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, AccessDenied, Warning
from datetime import date
from functools import reduce
import random
import datetime
import calendar
from dateutil.relativedelta import relativedelta


def get_years_field():
    year_list = []
    for i in range(2023, 2043):
        year_list.append((i, str(i)))
    return year_list


class BaoCaoGiaThanh(models.Model):
    _name = "casound.bao_cao_gia_thanh.wizard"
    _description = "Product Cost Report"
    thang = fields.Selection(
        [('01', 'Tháng 1'), ('02', 'Tháng 2'), ('03', 'Tháng 3'),
         ('04', 'Tháng 4'), ('05', 'Tháng 5'), ('06', 'Tháng 6'),
         ('07', 'Tháng 7'), ('08', 'Tháng 8'), ('09', 'Tháng 9'),
         ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')],
        string='Month', default=str(datetime.datetime.now().month)
    )
    nam = fields.Selection(
        [(str(r), str(r))
         for r in range(2022, datetime.datetime.now().year + 50)],
        string='Year',
        default=str(datetime.datetime.now().year),
    )

    def get_production_orders(self, product_id):
        production_orders = self.env['mrp.production'].search(
            [('product_id', '=', product_id)])
        return production_orders

    def print_report(self):
        data = {
            'model': 'casound.bao_cao_gia_thanh.wizard',
            'form_data': self.read()[0]
        }
        thang = int(data['form_data']['thang'])
        nam = int(data['form_data']['nam'])
        hoanthanh = 'done'
        product = "product"
        chiphi = "service"

        thanhpham = 13
        chinh = 7
        phu = 15
        chiphinhancong = 16
        chiphichung = 17
        start_date = datetime.date(nam, thang, 1)
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)
        # danh sach nhom san pham
        list_group = self.env['product.category'].search(
            [('active', '=', True) and ('parent_id', '=', False)])

        # danh sách sản phẩm và giá trị vốn
        list_thanh_pham = self.env['product.product'].search(
            [('active', '=', True) and ('detailed_type', '=', product) and ('is_finished', '=', True)])
        list_chi_phi_phan_bo = self.env['stock.landed.cost'].search([('state', '=', hoanthanh) and (
            'date', '>=', start_date) and ('date', '<=', start_date)])
        list_chi_phi_nhan_cong = self.env['stock.landed.cost'].search([('state', '=', hoanthanh) and (
            'date', '>=', start_date) and ('date', '<=', start_date)])
        list_chi_phi_chung = self.env['stock.landed.cost'].search(
            [('state', '=', hoanthanh) and ('categ_id', '=', chiphichung) and ('detailed_type', '=', chiphi) and (
                'date', '>=', start_date) and ('date', '<=', start_date)])
        lenhsanxuatmain = self.env['mrp.production'].search([])
        # result
        list_thanh_pham_models = []
        danhsachnhap = []
        soluongnhap = 0
        tondodang = 0
        tondodangcuoi = 0
        giatridodangdau = 0
        giatridodangcuoi = 0
        soluongnvlchinh = 0
        soluongnvlphu = 0
        chiphinhancongmain = 0
        chiphichungmain = 0
        first_day = datetime.date(nam, thang, 1)
        _, num_days = calendar.monthrange(nam, thang)
        last_day = datetime.date(nam, thang, num_days)

        tilenvlchinh = 0
        tilenvlphu = 0
        tilenhancong = 0
        tilechiphichung = 0
        totalbom = 0
        tongbom = 0  # tổng chi phí nvl
        bomchinh = 0  # chi phí nvl chính
        bomphu = 0  # chi phí nvl phụ
        giatrilenhsx = 0
        chiphinhancongfinal = 0
        chiphichungfinal = 0
        tong_chi_phi_lsx = 0
        tong_chi_phi_lsx_chua_san_pham = 0
        list_chi_chi = []

        # tổng chi phí là 100%. trong hàm này tính ra tỉ lệ của nvl chính, phụ và tỉ lệ chi phí nhân công, chi phí chung, sau đó nhân với tổng số lượng sản phẩm sản xuất trong kỳ
        if len(list_thanh_pham) != 0:
            for i in list_thanh_pham:
                print("id", i)
                danhsachthaydoi = i['stock_quant_ids']
                lenhsanxuat = self.env['mrp.production'].search(
                    [('product_id', '=', i.id)])
                # lấy ra danh sách nguyên vật liệu của sản phẩm
                listbom = i['bom_ids'][0]['bom_line_ids']
                print(listbom)

                # tính tỉ lệ nvl chính và phụ của sản phẩm dựa trên nhóm sản phẩm
                if len(listbom) != 0:
                    for tilebom in listbom:
                        print('m', type(tilebom['product_id']['categ_id'].id))
                        tongbom += tilebom['product_id']['standard_price'] * \
                                   tilebom['product_qty']
                        if tilebom['product_id']['is_main_material'] == True:
                            print("co bom chinh")
                            bomchinh += tilebom['product_id']['standard_price'] * \
                                        tilebom['product_qty']

                        if tilebom['product_id']['is_main_material'] == False:
                            print("co bom phu")
                            bomphu += tilebom['product_id']['standard_price'] * \
                                      tilebom['product_qty']
                if tongbom > 0:
                    tylebom = tongbom / i['standard_price']
                    tilenvlchinh = bomchinh / tongbom * tylebom
                    tilenvlphu = bomphu / tongbom * tylebom
                    totalbom = tongbom
                print("bom", tilenvlchinh)
                print("bom1", tilenvlphu)
                print("bom2", totalbom)
                print(lenhsanxuat)

                # Hàm tính toán số lượng sản phẩm được sản xuất trong tháng
                if len(danhsachthaydoi) != 0:
                    for phieu in danhsachthaydoi:
                        if phieu['quantity'] > 0 and phieu['in_date'].month == thang:
                            soluongnhap += phieu['quantity']
                        # nhân công
                if len(list_chi_phi_phan_bo) != 0:
                    for phanbo in list_chi_phi_phan_bo:
                        tong_chi_phi_nc = 0
                        tong_chi_phi_chung = 0
                        list_chi_chi = []
                        data = {}

                        if len(phanbo['mrp_production_ids']) != 0:

                            for m in phanbo['mrp_production_ids']:
                                tong_chi_phi_lsx += m['product_qty'] * \
                                                    m['product_id']['standard_price']  # 2
                                if m['product_id']['id'] == i.id:
                                    tong_chi_phi_lsx_chua_san_pham += m['product_qty'] * m['product_id'][
                                        'standard_price']  # 1

                        if len(phanbo['cost_lines']) != 0:
                            for cl in phanbo['cost_lines']:
                                chi_phi_tam = 0
                                list_product = []
                                for gr in list_group:

                                    # tổng chi phí của lệnh sản xuất
                                    if cl['product_id']['categ_id'] == gr.id:
                                        chi_phi_tam += cl['price_unit']  # 3
                                        list_product.append(gr)
                                if tong_chi_phi_lsx != 0:
                                    chiphithat = (
                                                         tong_chi_phi_lsx_chua_san_pham / tong_chi_phi_lsx) * chi_phi_tam
                                    data = {
                                        'cost': chiphithat,
                                        'name': cl['complete_name'],
                                        'list': list_product
                                    }
                                    list_chi_chi.append(data)
                                    data = {}
                                    list_product = []
                                    chi_phi_tam = 0

                                # tổng giá trị của lệnh sản xuất sản phẩm

                if len(lenhsanxuat) != 0:
                    for sanxuat in lenhsanxuat:
                        print(sanxuat)
                        #     listbomlsx = sanxuat['product_id']
                        giatrilenhsx += sanxuat['product_qty'] * \
                                        sanxuat['product_id']['standard_price']
                        if sanxuat['date_planned_start'].date() < first_day and (
                                sanxuat['state'] in ['confirmed', 'planned', 'progress']):
                            tondodang += sanxuat['product_qty']
                        if (sanxuat['state'] in ['confirmed', 'planned', 'progress']) and (
                                sanxuat['date_planned_start'].date() > last_day):
                            tondodangcuoi += sanxuat['product_qty']

                giatrungbinh = 0
                if soluongnhap != 0:
                    giatrungbinh = ((tongbom * (
                            soluongnhap + tondodang - tondodangcuoi)) + chiphichungfinal + chiphinhancongfinal) / soluongnhap

                value = {
                    "name": i['name'],
                    "masp": i['default_code'],
                    "soluongnhap": soluongnhap,
                    'giavon': giatrungbinh,
                    "giatridodangdau": tondodang * giatrungbinh,
                    "giatridodangcuoi": tondodangcuoi * giatrungbinh,
                    "tonggiathanh": soluongnhap * giatrungbinh + tondodang * giatrungbinh - tondodangcuoi * giatrungbinh,
                    'nvlchinh': bomchinh * (soluongnhap + tondodangcuoi),
                    'nvlphu': bomphu * (soluongnhap + tondodangcuoi),
                    'listchiphi': list_chi_chi,

                    'tongcong': giatrungbinh * (
                            soluongnhap + tondodangcuoi),

                }
                list_thanh_pham_models.append(value)

                soluongnhap = 0
                tondodang = 0
                tondodangcuoi = 0
                soluongnvlchinh = 0
                soluongnvlphu = 0
                tongbom = 0  # tổng chi phí nvl
                bomchinh = 0  # chi phí nvl chính
                bomphu = 0  # chi phí nvl phụ
                totalbom = 0
                giatrilenhsx = 0
            # giá trị vốn
            # list_unit_cost = self.env['stock.valuation.layer'].search([])
            # today = date.today().strftime("%d/%m/%Y")
            todayDate = datetime.date.today()
            if todayDate.day > 25:
                todayDate += datetime.timedelta(7)

            # diadiem = data['form_data']['loction_id']

            # if len(list_san_pham) != 0:
            #     for i in list_san_pham:
            #         print(i['name'])
            display = False

            if len(list_thanh_pham_models) != 0:
                display = True
            data['list_san_pham'] = list_thanh_pham_models
            data['thang'] = thang
            data['nam'] = nam

            data['display'] = display
            display_sub = False
            if len(list_chi_chi) != 0:
                display_sub = True
            data['leng'] = len(list_chi_chi) + 3
            data['display_sub'] = display_sub
            print(data)
        return self.env.ref("casound.action_bao_cao_gia_thanh_report").report_action(self, data=data)

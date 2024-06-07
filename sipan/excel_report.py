import io
import xlsxwriter

from account.models import User
from subscription.models import Subscription, Section, SectionYear


def generate_excel_report():
    start_col = 2
    start_row = 2
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sections = Section.objects.all()
    money = workbook.add_format({'num_format': '###,###,##0ريال'})
    text = workbook.add_format({'num_format': '@'})

    headers = [
        {
            "header": "Անդամակցութեան Համար"
        },
        {
            "header": "Սոց․ համար",
            "format": text
        },
        {
            "header": "Անուն",
            "format": text
        },
        {
            "header": "Ազգանուն",
            "format": text
        },
        {
            "header": "Անուն (Պարսկերեն)",
            "format": text
        },
        {
            "header": "Ազգանուն (Պարսկերեն)",
            "format": text
        },
        {
            "header": "Տան համար",
            "format": text
        },
        {
            "header": "Բջջային համար",
            "format": text
        },
        {
            "header": "Email",
            "format": text
        },
        {
            "header": "Հասցէ",
            "format": text
        }
    ]

    for section in sections:
        years = SectionYear.objects.filter(section=section.id)
        years_id = years.values_list('id')
        section_users_sub = Subscription.objects.filter(year__in=years_id)
        section_users_id = section_users_sub.values_list("user")
        section_users = User.objects.filter(id__in=section_users_id)

        datas = []
        worksheet = workbook.add_worksheet(section.name)
        years_info = [{'id': y.id, 'year': y.year, 'price': y.price} for y in years]
        
        for user in section_users:
            data = [
                user.id,
                user.national_code,
                user.first_name,
                user.last_name,
                user.first_name_fa,
                user.last_name_fa,
                user.home,
                user.phone,
                user.email,
                user.address,
            ]
            # print(user.phone)
            
            for y in years_info:
                if section_users_sub.filter(user=user.id, year=y['id']):
                    data.append(y['price'])
                else:
                    data.append(0)
                
            datas.append(data)
        
        options = { 
            "data": datas,
            'autofilter': False,
            "columns": headers + [{"header": str(y['year']), "format": money} for y in years_info]
        }
        if len(datas):
            worksheet.add_table(first_row=start_row, first_col=start_col, last_col=len(datas[0])+start_col-1, last_row=start_row+len(datas), options=options)
            worksheet.autofit()
        worksheet.set_column(start_col + len(headers), start_col + len(headers) + len(years_info), width=15)
    workbook.close()
    return output.getvalue()
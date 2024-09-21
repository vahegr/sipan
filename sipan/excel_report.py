import io
import xlsxwriter

from account.models import User
from subscription.models import Subscription, Section, SectionYear, History


def generate_excel_report():
    start_col = 2
    start_row = 2
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    money = workbook.add_format({'num_format': '###,###,##0ريال'})
    text = workbook.add_format({'num_format': '@'})
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    header_format = workbook.add_format({'bold': True, 'font_size': 32})

    headers = [
        {
            "header": "Անդամակցութեան Համար"
        },
        {
            "header": "From",
            "format": date_format
        },
        {
            "header": "To",
            "format": date_format
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

    sections = Section.objects.all()
    for section in sections:

        years = SectionYear.objects.filter(section=section.id)
        years_id = years.values_list('id')
        section_users_sub = Subscription.objects.filter(section_year__in=years_id)
        section_history = History.objects.filter(section=section)

        datas = []
        worksheet = workbook.add_worksheet(section.name)
        worksheet.write('B2', section.name, header_format)
        worksheet.set_column('B:B', -1)
        years_info = [{'id': y.id, 'year': y.year, 'price': y.price} for y in years]

        for history in section_history:
            user = history.user
            next_history = History.objects.filter(user=user, date_changed__gt=history.date_changed).order_by("-date_changed").first()
            next_history_str = next_history.date_changed if next_history else ""
            data = [
                user.id,
                history.date_changed,
                next_history_str,
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

            for y in years_info:
                sub = section_users_sub.filter(user=user.id, section_year=y['id']).first()
                if sub:
                    data.append(sub.amount)
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

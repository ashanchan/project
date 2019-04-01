import xlrd
import util.system as SYSTEM
import util.log as LOGGER
# ===================================================


def readData(url):
    # import excel sheet and get refernce of first sheet
    data = []
    try:
        LOGGER.show('info',('\tOpening data file %s' % url))
        workBook = xlrd.open_workbook(url, on_demand=True)
        workSheet = workBook.sheet_by_index(0)
        keys = [v.value for v in workSheet.row(0)]

        LOGGER.show('info',('\t\tProcessing data file '))
        for row_number in range(workSheet.nrows):
            row_data = {}
            for col_number, cell in enumerate(workSheet.row(row_number)):
                row_data[keys[col_number]] = cell.value
            if row_number == 0:
                continue
            else:
                data.append(row_data)

        workBook.release_resources()
        del workBook
    except:
        LOGGER.show('error',('\t\tFile Not Found : %s' % (url)))
        SYSTEM.exit()
    finally:
        return { 'data' : data}
# ===================================================

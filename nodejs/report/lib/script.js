var i = 0,
    numRows = 0,
    numCols = 0;
var options = {
    'title': '',
    'width': '100%',
    'height': 300,
    'is3D': true
};
//==================================================================
function init() {
    google.charts.load('current', {
        'packages': ['corechart']
    });
    google.charts.setOnLoadCallback(drawChart);
}
//==================================================================
function drawChart() {
    renderCourseGraph();
    renderLessonGraph();
}
//==================================================================
function renderCourseGraph() {
    var dataTable = new google.visualization.DataTable();
    var graphData = [];
    graphData.push(['Report', 'Data']);
    for (var data in reportData.course) {
        graphData.push([data, reportData.course[data]]);
    }
    //=== determine the number of rows and columns.
    numRows = graphData.length;
    numCols = graphData[0].length;
    //=== add columns
    dataTable.addColumn('string', graphData[0][0]);
    for (i = 1; i < numCols; i++) {
        dataTable.addColumn('number', graphData[0][i]);
    }
    //=== add rows
    for (i = 1; i < numRows; i++) {
        dataTable.addRow(graphData[i]);
    }
    //===
    options.title = 'Overall Testout Result';
    //===
    var chart = new google.visualization.PieChart(document.getElementById('COURSE_CHART_DIV'));
    chart.draw(dataTable, options);
}
//==================================================================
function renderLessonGraph(flag) {
    var dataTable = new google.visualization.DataTable();
    var graphData = [];
    graphData.push(['Results', 'Pass', 'Fail']);
    for (var data in reportData.lesson) {
        graphData.push([reportData.lesson[data].title, reportData.lesson[data].passedId.length, reportData.lesson[data].failedId.length]);
    }
    //=== determine the number of rows and columns.
    numRows = graphData.length;
    numCols = graphData[0].length;
    //=== add columns
    dataTable.addColumn('string', graphData[0][0]);
    for (i = 1; i < numCols; i++) {
        dataTable.addColumn('number', graphData[0][i]);
    }
    //=== add rows
    for (i = 1; i < numRows; i++) {
        dataTable.addRow(graphData[i]);
    }
    //===
    options.title = 'Lesson-wise Report';
    var chart = new google.visualization.BarChart(document.getElementById('LESSON_CHART_DIV'));
    chart.draw(dataTable, options);
}
//==================================================================
function toggleData(event) {
    for (var el of document.querySelectorAll('.js-data-holder')) {
        el.style.display = event.currentTarget.checked ? 'block' : 'none';
    }
}
//==================================================================
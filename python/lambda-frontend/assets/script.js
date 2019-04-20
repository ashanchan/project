/*jshint sub:true*/
query = '';
//=================================================
function getTweetSentiment() {
    query = $('#findSentiment').val();
    if (validateQuery(query)) {
        dataQuery = JSON.stringify({ 'findSentiment': query });
        $('#data-loader').removeClass('hidden');
        $('#data-holder').addClass("hidden");
        connectToLambda('https://e4bj5aj4d8.execute-api.ap-south-1.amazonaws.com/prod', dataQuery, showTweet);
    }
}
//=================================================
function showTweet(data) {
    $('#results').html('');
    $('#table').html('');

    dCtr = data.length;
    pCtr = 0;
    sCtr = 0;

    var line = '<table class="w3-table-all w3-hoverable">';
    line += '<tr class="w3-blue">';
    line += '<th>Tweets</th>';
    line += '<th>Polarity</th>';
    line += '<th>Subjectivity</th>';
    line += '</tr>';
    data.forEach(function(tweet) {
        line += '<tr>';
        line += '<td>' + tweet['tweet'] + '</td>';
        line += '<td><span class="w3-small w3-teal w3-right">' + String(tweet['polarity']).substring(0, 5) + '</span></td>';
        line += '<td><span class="w3-small w3-blue w3-right">' + String(tweet['subjectivity']).substring(0, 5) + '</span></td>';
        line += '</tr>';
        pCtr += tweet['polarity'];
        sCtr += tweet['subjectivity'];
    });
    line += '</table>';

    $('#table').append(line);
    $('#results').append('<div class="w3-bar-item">Sampled Tweet : ' + query + '</div>');
    $('#results').append('<div class="w3-bar-item">Total Samples : ' + dCtr + '</div>');
    $('#results').append('<div class="w3-bar-item">Total Polarity : ' + (pCtr / dCtr) + '</div>');
    $('#results').append('<div class="w3-bar-item">Total Subjectivity : ' + (sCtr / dCtr) + '</div>');

    $('#data-loader').addClass("hidden");
    $('#data-holder').removeClass("hidden");
}
//=================================================
function getTranslation() {
    query = $('input[name=mode]:checked').val();
    if (validateQuery(query)) {
        dataQuery = JSON.stringify({ 'mode': query });
        $('#data-loader').removeClass('hidden');
        $('#data-holder').addClass("hidden");
        connectToLambda('https://ld10wcycm2.execute-api.ap-south-1.amazonaws.com/prod', query, showTranslation);
    }
    event.preventDefault();
}
//=================================================
function showTranslation(data) {
    $('#results').append('<div class="w3-bar-item"><a href= "' + data[0]['filePath'] + '" target="_blank">no-translation.txt</div>');
    $('#results').append('<div class="w3-bar-item"><a href= "' + data[1]['filePath'] + '" target="_blank">messages.zip</div>');
    $('#data-loader').addClass("hidden");
    $('#data-holder').removeClass("hidden");
}
//=================================================
function validateQuery(query) {
    event.preventDefault();
    return query.trim().length > 0;
}
//=================================================
function connectToLambda(url, query, callback) {
    if (query.trim().length > 0) {
        $.ajax({
            method: 'POST',
            url: url,
            dataType: 'json',
            data: query,
            headers: {
                'Content-Type': 'application/json'
            },
            success: function(data) {
                callback(data);
            }
        });
    }
}
//=================================================
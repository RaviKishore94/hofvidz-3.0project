var delayTimer;
$('#id_search_term').keyup(function() {
    clearTimeout(delayTimer);
    $('#search_results').text('Loading...');
    delayTimer = setTimeout(function() {
        var text = $('#id_search_term').val();
        $.ajax({
            url: '/video/search/',
            data: {
                'search_term': text
            },
            dataType: 'json',
            success: function(data) {
                var results = '';
                $('#search_results').text('');
                results += '<div class="row">';
                data['items'].forEach(function(video) {
                    results += '<div class="col-md-4 mt-3"><div class="card mb-4 shadow-sm">';
                    results += '<iframe width="100%" height="225" src="https://www.youtube.com/embed/' + video['id']['videoId'] + '" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
                    results += '<div class="card-body"><p class="card-text">' + video['snippet']['title'] + '</p>'
                    results += '<a href="#" class="btn btn-primary" onclick="addVideo(\'' + video['id']['videoId'] + '\')">Add</a>'
                    results += '</div></div></div>'
                });
                results += '</div>';
                $('#search_results').append(results);
                //$('#search_results').text(data['error']);
            }
        });
    }, 1000);
});

function addVideo(video_id) {
    $('#id_url').val('https://www.youtube.com/watch?v=' + video_id);
    $('#submit_video').submit();
}
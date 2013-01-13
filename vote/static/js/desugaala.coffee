apiCall = (opts) -> _.defaults {}, opts, 
  type: 'POST'
  headers:
    "X-CSRFToken": window.desugaalaCsrfToken
    "Content-Type": "application/json"

serializeBallot = ->
  ballot = []

  for categoryEl in $('.category')
    $category = $(categoryEl)
    category = $category.data 'category'

    console?.log 'category', category

    options = []

    for optionEl in $category.find('li')
      $option = $(optionEl)
      if $option.is '.deadline'
        console?.log 'deadline'
      else
        option = $option.data 'option'
        console?.log ' - option', option
        options.push option
    
    ballot['category'] = options if options.length > 0

  url: '/vote'
  data: JSON.stringify
    ballot: ballot
    username: $('#id_username').val()
    password: $('#id_password').val()

$ ->
  $('.category').sortable().disableSelection()

  _loggedInState = $('#login-button')
    .asEventStream('click').doAction((e) -> false)
    .merge($('#login-form').asEventStream('submit').doAction((e) -> false))
    .map ->
      console?.log 'klak'

      username: $('#id_username').val()
      password: $('#id_password').val()
    .map (data) ->
      url: '/login'
      data: JSON.stringify data
    .map(apiCall)
    .ajax()
    .map('.result')
    .toProperty('not_yet_logged_in')

  _loggedInState.onValue (v) -> console?.log '_loggedInState', v

  _loginOk = _loggedInState.map((v) -> v == 'ok')
  _loginOk.assign $('#send-button'), 'toggle'
  _loginOk.assign $('.login-ok'), 'toggle'
  _loginOk.not().assign $('#login-form'), 'toggle'

  _loggedInState.map((v) -> v == 'login_failed' or v == 'not_yet_logged_in')
    .assign $('#not-logged-in'), 'toggle'

  _loggedInState.map((v) -> v == 'login_failed')
    .assign $('.login-failed'), 'toggle'

  _loggedInState.map((v) -> v == 'already_voted')
    .assign $('.already-voted'), 'toggle'

  $('#send-button').asEventStream('click')
    .filter(_loginOk)
    .map(serializeBallot)
    .map(apiCall)
    .ajax()
    .onValue (v) -> console?.log '/vote response', v
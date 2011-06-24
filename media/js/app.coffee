app = tire.app


app.config =
  apiUrl: '/api/1.0/'
  rpc: false
  webapp: false


# Format: [window addressbar match, name of controller function]
app.routes = [
  [/^$/, 'main']
  [/(\w+)\/(page(\d+))?/, 'section']
  [/(\w+)\/(\d+)(#(\d+))?/, 'thread']
  [/settings/, 'settings']
  [/feed/, 'feed']
]
  

# Functions would be executed when user will navigate to the other page.
app.controllers =
  main: -> null
  section: (slug, _, page = 0) -> null
  thread: (slug, opPost, _, startFrom) ->
    app.api.subscribe("feed/#{app.page.threadId}")
  settings: -> null
  feed: -> null


app.api.onData = ({posts}) ->
  return unless posts
  for post in posts
    $post = $(post)
    $post = $([$post.get(0), $post.get(2)])  # $post[1] is text node
      .hide()
      .appendTo('.thread')
      .fadeIn 500, (event) ->
        $(event.currentTarget).attr('style', '')
    $post.find('.tripcode:contains("!")').addClass('staff')
    app.posts.init($post)
    text = $post.find('.message').text()
    app.notification("#{app.page.section}/#{app.page.first}: #{text}")


class Elem
  _dataAttr: (elem, name) -> @["_#{name}"] ?= parseInt(elem.attr("data-#{name}"), 10)

class Post extends Elem
  # post - jQuery instance of post
  constructor: (@post) -> null
  thread: ->
    @_thread ?= if app.page.type is 'thread'
      app.page.cache.thread
    else
      @post.closest('.thread')

  first: ->
    @_first ?= if app.page.type is 'thread'
      app.page.cache.first
    else
      @thread().find('.post:first')

  id: -> @_dataAttr('id')
  pid: -> @_dataAttr('pid')


class Thread extends Elem
  constructor: (@thread) -> null
  first: ->
    @_first ?= if app.page.type is 'thread'
      app.page.cache.first
    else
      @thread.find('.post:first')

  posts: -> @_posts ?= @thread.find('.post')
  id: -> @_dataAttr('id')

class 

  


# Application actions, separated into 'modules' (main, message, roster etc).
app.acts.main = 
  doSomething: -> null
  logout: ->
    app.cookie('id', null)
    app.path.redirect('/login')


app.hotkeys.init = ->
  # Send message on enter.
  $('#item').delegate '.text', 'keyup', (event) =>
    return true unless event.which is @codes.return
    app.acts.main.doSomething()


# Events and window styling.
app.events =
  changeSidebarWidth: (width) ->
    $('.sidebar').css('width', width)
    $('.main').css('left', width)

  init: ->
    $('#logout').click(app.acts.main.logout)


# Call 'init' functions in this modules.
app.init(['events', 'hotkeys'])
window.app = app
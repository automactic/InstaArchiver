import { Component, OnInit, OnDestroy } from '@angular/core';
import { webSocket } from 'rxjs/webSocket';

enum Event {
  post_create = "post.create",
  post_saved = "post.saved",
  post_not_found = "post.not_found",
}

interface Post {
  shortcode: string
  owner_username: string
  creation_time: Date
}

class PostActivity {
  event: Event
  shortcode: string
  post?: Post

  constructor(event: Event, shortcode: string) {
    this.event = event
    this.shortcode = shortcode
  }
}

@Component({
  selector: 'app-archive',
  templateUrl: './archive.component.html',
  styleUrls: ['./archive.component.scss']
})
export class ArchiveComponent implements OnInit {
  shortcode?: string

  activities: string[] = []
  latest_event = new Map<string, Event>()
  posts = new Map<string, Post>()

  socket = webSocket<PostActivity>('ws://localhost:37500/web_socket/posts/')

  constructor() { }
  
  ngOnInit(): void {
    this.socket.subscribe(activity => {
      if (activity.event == Event.post_saved && activity.post) {
        this.latest_event.set(activity.shortcode, activity.event)
        this.posts.set(activity.shortcode, activity.post)
      }
    })
  }
  
  ngOnDestroy() {
    this.socket.complete()
  }

  onSubmit() {
    if (this.shortcode) {
      let activity = new PostActivity(Event.post_create, this.shortcode)
      this.socket.next(activity)
      
      this.latest_event.set(this.shortcode, activity.event)
      this.activities.push(this.shortcode)
      
      this.shortcode = undefined
    }
  }
}

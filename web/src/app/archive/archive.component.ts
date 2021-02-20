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

class Activity {
  event: Event
  shortcode: string
  post?: Post
  message?: string

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

  shortcodes: string[] = []
  activities = new Map<string, Activity>()

  socket = webSocket<Activity>('ws://localhost:37500/web_socket/posts/')
  constructor() { }
  
  ngOnInit(): void {
    this.socket.subscribe(activity => {
      this.activities.set(activity.shortcode, activity)
    })
  }
  
  ngOnDestroy() {
    this.socket.complete()
  }

  onSubmit() {
    if (this.shortcode) {
      let activity = new Activity(Event.post_create, this.shortcode)
      this.socket.next(activity)
      
      this.shortcodes.push(this.shortcode)
      this.activities.set(this.shortcode, activity)

      this.shortcode = undefined
    }
  }
}

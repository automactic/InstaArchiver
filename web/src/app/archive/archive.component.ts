import { Component, OnInit, OnDestroy } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

import { environment } from './../../environments/environment';

enum Event {
  post_create = "post.create",
  post_saved = "post.saved",
  post_not_found = "post.not_found",
}

interface Post {
  shortcode: string
  username: string
  timestamp: Date
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
export class ArchiveComponent implements OnInit, OnDestroy {
  shortcode?: string

  shortcodes: string[] = []
  activities = new Map<string, Activity>()

  socket: WebSocketSubject<Activity>
  constructor() {
    let host = environment.production ? window.location.host : 'localhost:37500'
    let url = 'ws://' + host + '/web_socket/posts/'
    this.socket = webSocket<Activity>(url)
  }
  
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

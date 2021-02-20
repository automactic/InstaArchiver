import { Component, OnInit, OnDestroy } from '@angular/core';
import { webSocket } from 'rxjs/webSocket';

class PostActivity {
  event: string;
  shortcode: string;

  constructor(event: string, shortcode: string) {
    this.event = event;
    this.shortcode = shortcode;
  }
}

@Component({
  selector: 'app-archive',
  templateUrl: './archive.component.html',
  styleUrls: ['./archive.component.scss']
})
export class ArchiveComponent implements OnInit {
  shortcode?: string;
  activities: PostActivity[] = [];

  socket = webSocket<PostActivity>('ws://localhost:37500/web_socket/posts/')

  constructor() { }
  
  ngOnInit(): void {
    this.socket.subscribe(activity => {
      this.activities.push(activity);
    })
  }
  
  ngOnDestroy() {
    this.socket.complete()
  }

  onSubmit() {
    if (this.shortcode) {
      this.socket.next({'event': 'post.create', 'shortcode': this.shortcode})
    }
  }
}

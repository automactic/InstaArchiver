import { Component, OnInit, OnDestroy } from '@angular/core';
import { webSocket } from 'rxjs/webSocket';

class Activity {
  shortcode: string;

  constructor(shortcode: string) {
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
  socket = webSocket('ws://localhost:37500/web_socket/posts/')

  constructor() { }
  
  ngOnInit(): void {
    this.socket.subscribe(data => {
      console.log(data)
    })
  }
  
  ngOnDestroy() {
    this.socket.complete()
  }

  onSubmit() {
    if (this.shortcode) {
      this.socket.next({'shortcode': this.shortcode})
    }
  }
}

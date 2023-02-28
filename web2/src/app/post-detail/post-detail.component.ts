import { Component, Input } from '@angular/core';

import { Post, PostService } from '../services/post.service';

@Component({
  selector: 'post-detail',
  templateUrl: './post-detail.component.html',
  styleUrls: ['./post-detail.component.scss']
})
export class PostDetailComponent {
  @Input() post?: Post
  postService: PostService

  constructor(postService: PostService) {
    this.postService = postService
  }
}

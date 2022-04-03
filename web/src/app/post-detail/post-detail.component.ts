import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

import { PostService, Post } from '../services/post.service';

@Component({
  selector: 'post-detail',
  templateUrl: './post-detail.component.html',
  styleUrls: ['./post-detail.component.scss']
})
export class PostDetailComponent implements OnChanges {
  @Input() shortcode?: string
  post?: Post
  postService: PostService

  constructor(postService: PostService) {
    this.postService = postService
  }

  ngOnChanges(changes: SimpleChanges) {
    this.post = this.postService.get(changes['shortcode'].currentValue)
  }
}

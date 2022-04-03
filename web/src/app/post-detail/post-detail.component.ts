import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

import { PostService, Post, PostItem } from '../services/post.service';

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

  delete(post: Post, item: PostItem) {
    this.postService.delete(post.shortcode, item.index).subscribe( _ => {
      // if (post.items.length == 1) {
      //   this.posts.splice(postIndex, 1);
      // } else {
      //   post.items.splice(itemIndex, 1);
      // }
    })
  }
}

import { Component, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Post, PostService } from '../services/post.service';

@Component({
  selector: 'post-detail',
  templateUrl: './post-detail.component.html',
  styleUrls: ['./post-detail.component.scss']
})
export class PostDetailComponent {
  @Input() post?: Post
  postService: PostService

  constructor(private route: ActivatedRoute, postService: PostService) {
    this.postService = postService
  }

  deleteItem(shortcode: string, itemIndex: number) {
    this.postService.deleteItem(shortcode, itemIndex).subscribe(_ => {
      this.post?.items.forEach((item, index, array) => {
        if (item.index == itemIndex) {
          array.splice(index, 1)
        }
      })
    })
  }
}

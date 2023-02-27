import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Post, PostService } from '../services/post.service';

@Component({
  selector: 'app-post-detail',
  templateUrl: './post-detail.component.html',
  styleUrls: ['./post-detail.component.scss']
})
export class PostDetailComponent {
  post?: Post;
  postService: PostService;

  constructor(private route: ActivatedRoute, postService: PostService) {
    this.postService = postService
    this.route.paramMap.subscribe(params => {
      let shortcode = params.get('shortcode')
      if (shortcode) {
        this.post = postService.get(shortcode)
      }
    })
  }
}

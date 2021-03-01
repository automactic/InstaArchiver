import { Component, OnInit } from '@angular/core';

import { Post, PostService } from '../services/post.service';
import { ProfileService } from '../services/profile.service';


@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.scss']
})
export class PostsComponent implements OnInit {
  postService: PostService;
  profileService: ProfileService;

  posts: Post[] = [];
  
  constructor(postService: PostService, profileService: ProfileService) {
    this.postService = postService;
    this.profileService = profileService;
  }

  ngOnInit(): void {
    this.loadNext()
  }

  loadNext() {
    this.postService.list(this.posts.length, 20).subscribe( response_data => {
      this.posts = this.posts.concat(response_data.posts);
    })
  }
}
